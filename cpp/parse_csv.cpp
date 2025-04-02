#include "../cpp/parse_csv.h"
#include "../cpp/tag_dir.h"

// ----- CSV Parsing -----
std::vector<WeatherPoint> parse_csv(const std::string& filepath) {
    std::vector<WeatherPoint> data;
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "[ERROR] Cannot open: " << filepath << '\n';
        return data;
    }

    std::string line;
    std::getline(file, line); // skip header

    while (std::getline(file, line)) {
        std::istringstream ss(line);
        std::string token;

        std::getline(ss, token, ','); // date
        std::getline(ss, token, ','); // time

        WeatherPoint wp;

        std::getline(ss, token, ',');
        if (token.empty()) continue;
        wp.temperature = std::stof(token);

        std::getline(ss, token, ',');
        if (token.empty()) continue;
        wp.humidity = std::stof(token);

        std::getline(ss, token, ',');
        if (token.empty()) continue;
        wp.pressure = std::stof(token);

        std::getline(ss, token, ','); // weather description (ignored)

        data.push_back(wp);
    }

    return data;
}

// ----- Recursive File Search -----
std::vector<std::string> find_all_csv_files(const std::string& root_dir) {
    std::vector<std::string> files;
    for (const auto& entry : fs::recursive_directory_iterator(root_dir)) {
        if (entry.is_regular_file() && entry.path().filename() == "weather_data.csv") {
            files.push_back(entry.path().string());
        }
    }
    return files;
}



// ----- Binary Writer -----
void write_binary(const std::string& output_path, const std::vector<WeatherPoint>& points) {
    std::ofstream out(output_path, std::ios::binary);
    if (!out.is_open()) {
        std::cerr << "[ERROR] Cannot write to: " << output_path << '\n';
        return;
    }

    uint32_t count = static_cast<uint32_t>(points.size());
    out.write(reinterpret_cast<const char*>(&count), sizeof(uint32_t));
    out.write(reinterpret_cast<const char*>(points.data()), count * sizeof(WeatherPoint));
    out.close();
}

// ----- Exported Wrapper Function -----
extern "C" __declspec(dllexport) void __stdcall package_csvs_to_bin(const char* input_dir, const char* output_file) {
    std::string input(input_dir);
    std::string output(output_file);

    std::vector<std::string> files = find_all_csv_files(input);
    std::vector<WeatherPoint> all_points;

    for (const auto& file : files) {
        auto points = parse_csv(file);
        all_points.insert(all_points.end(), points.begin(), points.end());
    }

    std::cout << "[INFO] Parsed " << all_points.size() << " weather points\n";

    process_weather_with_cuda(all_points);
    write_binary(output, all_points);

    std::cout << "[INFO] Binary data written to " << output << std::endl;
}




