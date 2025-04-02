#include "../cpp/tag_dir.h"


std::string output_path = "AI/Reports/code_summary_results.json";
const char* command = "python python/list_directory_full.py";
int result = std::system(command);
json jsonData;
std::vector<std::string> files;


// Ensure only valid extensions are processed
std::unordered_set<std::string> valid_extensions = {
    ".txt", ".cpp", ".c", ".h", ".hpp", ".cu", ".cuh",         
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",               
    ".cs", ".go", ".swift", ".rs", ".kt", ".kts",              
    ".html", ".htm", ".css", ".sh", ".bash", ".bat", 
    ".cmd", ".json", ".xml", ".yaml", ".yml", ".ini",
	".csv", ".tsv", ".log", ".md", ".rst", ".adoc", ".tex",
    ".org", ".sql", ".m", ".r", ".pl", ".rb", ".lua"

};

std::string preprocess_docx_text(const std::string& text) {
    std::string result = text;
    result.erase(std::remove(result.begin(), result.end(), '\r'), result.end());
    std::transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

json build_json_summary(const std::vector<int>& counts,
    const std::vector<std::vector<int>>& positions,
    const std::vector<std::string>& tags) {
    json summary;
    for (size_t i = 0; i < tags.size(); i++) {
        if (counts[i] > 0) {
            summary[tags[i]] = positions[i]; // Assumes JSON supports vector<int> conversion.
        }
    }
    return summary;
}


// Process a directory of code files using CUDA
void process_directory_code(const std::string& directory, const std::string& tag_file, const std::string& code_file) {
    // Read both tag files.
    std::vector<std::string> tags1 = read_txt(tag_file);
    std::vector<std::string> tags2 = read_txt(code_file);
    std::vector<std::string> tags = tags1;
    tags.insert(tags.end(), tags2.begin(), tags2.end());

    if (!fs::exists(directory) || !fs::is_directory(directory)) {
        std::cerr << "[ERROR] Invalid directory: " << directory << std::endl;
        return;
    }

    json jsonData;
    std::error_code ec;
    fs::recursive_directory_iterator it(directory, fs::directory_options::skip_permission_denied, ec), end;

    while (it != end) {
        if (fs::is_regular_file(*it)) {
            std::string ext = it->path().extension().string();
            std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower); // Normalize to lowercase

            if (valid_extensions.find(ext) != valid_extensions.end()) {
                // Read file lines and build a single string of file content
                std::vector<std::string> lines = read_txt(it->path().string());
                std::string file_content;
                file_content.reserve(lines.size() * 100); // Estimate average line length to optimize memory usage

                for (const auto& line : lines) {
                    file_content += line;
                    file_content += '\n';
                }


                // --- 1. Get aggregate count information using CUDA ---
                std::vector<int> counts(tags.size(), 0);
                process_text_with_cuda(file_content, tags, counts);
                json counts_json;
                for (size_t i = 0; i < tags.size(); i++) {
                    if (counts[i] > 0) {
                        counts_json[tags[i]] = counts[i];
                    }
                }

                // --- 2. Get detailed per-line tagging information ---
                // Create a tag map where each tag is its own category
                std::unordered_map<std::string, std::vector<std::string>> tag_map;
                for (const auto& t : tags) {
                    tag_map[t].push_back(t);
                }
                json lines_json = process_text_files(it->path().string(), tag_map);

                // --- 3. Combine both results ---
                json file_result;
                file_result["counts"] = counts_json;
                // process_text_files returns a JSON with a "summary" key holding the details
                file_result["lines"] = lines_json.contains("summary") ? lines_json["summary"] : json();

                // Only add if there is at least one match
                if (!file_result["counts"].empty() || !file_result["lines"].empty()) {
                    jsonData[it->path().string()] = file_result;
                }
            }
        }

        it.increment(ec);
    }

    // Save results to JSON file
    std::ofstream output_file(output_path);
    if (!output_file) {
        std::cerr << "[ERROR] Cannot open output file: " << output_path << std::endl;
        return;
    }

    try {
        output_file << jsonData.dump(4);
        std::cout << "Results saved to " << output_path << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to write JSON: " << e.what() << std::endl;
    }

}

// Execute a Python script to list directory contents
void get_list_directory_full() {
    
    result = std::system(command);
    if (result == -1) {
        std::cerr << "[ERROR] System command execution failed!" << std::endl;
    }
    else if (result != 0) {
        std::cerr << "[ERROR] Python script failed with exit code " << result << std::endl;
    }
	else {
		std::cout << "[INFO] Python script executed successfully." << std::endl;
	}
}

// Windows DLL entry point
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

// DLL Exported `run` Function
extern "C" {
    __declspec(dllexport) void __stdcall run(const char* dir, const char* tag_file, const char* code_file) {
        std::string directory = dir;
        get_list_directory_full();
        process_directory_code(directory, tag_file, code_file);
        std::cout << "[INFO] Program executed successfully." << std::endl;
    }
}
