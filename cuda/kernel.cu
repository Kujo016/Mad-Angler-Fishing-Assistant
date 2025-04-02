#include "../cuda/kernel.cuh"





// ✅ GPU Kernel: Checks if a keyword exists in each line
__device__ bool contains(const char* line, const char* keyword) {
    int i = 0;
    while (line[i] != '\0') {
        int j = 0;
        while (line[i + j] != '\0' && keyword[j] != '\0' && line[i + j] == keyword[j]) {
            j++;
        }
        if (keyword[j] == '\0') return true;
        i++;
    }
    return false;
}

// ✅ CUDA Kernel for text tagging
__global__ void tag_text_lines(char* lines, char* keywords, int* results, int num_lines, int num_keywords, int max_line_length) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    if (idx < num_lines) {
        char* line = lines + idx * max_line_length;

        for (int k = 0; k < num_keywords; k++) {
            char* keyword = keywords + k * 32;  // Max keyword length of 32
            if (contains(line, keyword)) {
                results[idx] = k + 1;  // Store keyword index if found
            }
        }
    }
}

// ✅ Read a text file and return its lines as a vector
std::vector<std::string> read_txt(const std::string& filepath) {
    std::vector<std::string> lines;
    std::ifstream file(filepath, std::ios::binary); // Open in binary mode to avoid newline conversion

    if (!file) {
        std::cerr << "[ERROR] Cannot open file: " << filepath << std::endl;
        return lines; // Return empty vector
    }

    std::string line;
    while (std::getline(file, line)) {
        // ✅ Remove invalid UTF-8 characters
        std::string sanitizedLine = removeInvalidUtf8(line);

        // ✅ Ignore completely empty lines
        if (!sanitizedLine.empty()) {
            lines.push_back(sanitizedLine);
        }
    }

    file.close();
    return lines;
}

// ✅ Remove invalid UTF-8 sequences from a string
std::string removeInvalidUtf8(const std::string& input) {
    std::string output;
    int i = 0;
    while (i < input.size()) {
        unsigned char c = static_cast<unsigned char>(input[i]);
        if (c < 0x80) {  // ASCII characters (valid)
            output += c;
            i++;
        }
        else if ((c & 0xE0) == 0xC0 && i + 1 < input.size() &&
            (static_cast<unsigned char>(input[i + 1]) & 0xC0) == 0x80) {
            // ✅ Valid 2-byte UTF-8 sequence
            output += input[i];
            output += input[i + 1];
            i += 2;
        }
        else if ((c & 0xF0) == 0xE0 && i + 2 < input.size() &&
            (static_cast<unsigned char>(input[i + 1]) & 0xC0) == 0x80 &&
            (static_cast<unsigned char>(input[i + 2]) & 0xC0) == 0x80) {
            // ✅ Valid 3-byte UTF-8 sequence
            output += input[i];
            output += input[i + 1];
            output += input[i + 2];
            i += 3;
        }
        else if ((c & 0xF8) == 0xF0 && i + 3 < input.size() &&
            (static_cast<unsigned char>(input[i + 1]) & 0xC0) == 0x80 &&
            (static_cast<unsigned char>(input[i + 2]) & 0xC0) == 0x80 &&
            (static_cast<unsigned char>(input[i + 3]) & 0xC0) == 0x80) {
            // ✅ Valid 4-byte UTF-8 sequence
            output += input[i];
            output += input[i + 1];
            output += input[i + 2];
            output += input[i + 3];
            i += 4;
        }
        else {
            // ❌ Invalid UTF-8 character: Skip it
            std::cerr << "[WARNING] Removed invalid UTF-8 byte: " << std::hex << static_cast<int>(c) << std::dec << std::endl;
            i++;
        }
    }
    return output;
}

// ✅ Process text files with CUDA
__host__ json process_text_files(const std::string& filepath, const std::unordered_map<std::string, std::vector<std::string>>& tags) {
    std::vector<std::string> lines = read_txt(filepath);
    int num_lines = static_cast<int>(lines.size());
    if (num_lines == 0 || tags.empty()) return json();

    // Flatten the tag list into keyword and category arrays
    std::vector<std::string> keyword_list, category_list;
    for (const auto& kv : tags) {
        const std::string& category = kv.first;
        for (const std::string& keyword : kv.second) {
            std::string lower_keyword = keyword;
            std::transform(lower_keyword.begin(), lower_keyword.end(), lower_keyword.begin(), ::tolower);
            keyword_list.push_back(lower_keyword);
            category_list.push_back(category);
        }
    }

    int num_keywords = static_cast<int>(keyword_list.size());
    if (num_keywords == 0) return json();

    // ✅ Allocate CPU memory
    char* h_lines = new char[num_lines * MAX_LINE_LENGTH]();
    char* h_keywords = new char[num_keywords * 32]();
    int* h_results = new int[num_lines]();

    // ✅ Copy lines & keywords to buffers
    for (int i = 0; i < num_lines; i++) {
        std::string lower_line = lines[i];
        std::transform(lower_line.begin(), lower_line.end(), lower_line.begin(), ::tolower);
        strncpy(h_lines + i * MAX_LINE_LENGTH, lower_line.c_str(), MAX_LINE_LENGTH - 1);
    }
    for (int i = 0; i < num_keywords; i++) {
        strncpy(h_keywords + i * 32, keyword_list[i].c_str(), 31);
        h_keywords[i * 32 + 31] = '\0';
    }

    // ✅ Allocate GPU memory
    char* d_lines, * d_keywords;
    int* d_results;
    cudaMalloc(&d_lines, num_lines * MAX_LINE_LENGTH);
    cudaMalloc(&d_keywords, num_keywords * 32);
    cudaMalloc(&d_results, num_lines * sizeof(int));
    cudaMemset(d_results, 0, num_lines * sizeof(int));


    cudaMemcpy(d_lines, h_lines, num_lines * MAX_LINE_LENGTH, cudaMemcpyHostToDevice);
    cudaMemcpy(d_keywords, h_keywords, num_keywords * 32, cudaMemcpyHostToDevice);
    cudaMemcpy(d_results, h_results, num_lines * sizeof(int), cudaMemcpyHostToDevice);

    // ✅ Define CUDA launch parameters
    int threadsPerBlock = 256;
    int blocksPerGrid = (num_lines + threadsPerBlock - 1) / threadsPerBlock;

    // ✅ Launch CUDA Kernel
    tag_text_lines << <blocksPerGrid, threadsPerBlock >> > (d_lines, d_keywords, d_results, num_lines, num_keywords, MAX_LINE_LENGTH);
    cudaDeviceSynchronize();

    // ✅ Copy results back from GPU
    cudaMemcpy(h_results, d_results, num_lines * sizeof(int), cudaMemcpyDeviceToHost);

    // ✅ Populate JSON output
    json output, summary;
    bool foundMatch = false;
    for (int i = 0; i < num_lines; i++) {
        std::string sanitizedLine = removeInvalidUtf8(lines[i]);
        // Check for a valid match: > 0 and within range
        if (h_results[i] > 0 && h_results[i] <= num_keywords) {
            foundMatch = true;
            // Adjust the index by subtracting 1 since we stored k+1
            std::string matched_category = category_list[h_results[i] - 1];
            summary[matched_category].push_back(sanitizedLine);
        }
    }
    output["summary"] = foundMatch ? summary : json({ {"error", "No matches found"} });


    // ✅ Free memory
    cudaFree(d_lines);
    cudaFree(d_keywords);
    cudaFree(d_results);
    delete[] h_lines;
    delete[] h_keywords;
    delete[] h_results;

    return output;
}

// ✅ CUDA Kernel to extract keyword matches from text data
__global__ void extract_tags_kernel(char* fileData, int fileSize, char* tags, int* tagOffsets, int numTags, int* results) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= fileSize) return; // Ensure within file bounds

    for (int t = 0; t < numTags; t++) {
        // Use provided tagOffsets if available, else compute offset as t * MAX_KEYWORD_LENGTH
        int tagStart = (tagOffsets != nullptr) ? tagOffsets[t] : t * MAX_KEYWORD_LENGTH;
        char* keyword = &tags[tagStart];

        // Check if keyword is found at this position
        int j = 0;
        while (keyword[j] != '\0' && fileData[idx + j] == keyword[j]) {
            j++;
        }

        if (keyword[j] == '\0') {
            // Mark match in results array
            atomicAdd(&results[t], 1);
        }
    }
}

// ✅ Extract Tags from CUDA processing
void load_tags_cuda(const std::string& filepath, std::unordered_set<std::string>& tags) {
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "[ERROR] Cannot open file: " << filepath << std::endl;
        return;
    }

    size_t fileSize = file.tellg();
    file.seekg(0);
    std::vector<char> fileData(fileSize);
    file.read(fileData.data(), fileSize);
    file.close();

    char* d_fileData;
    cudaMalloc((void**)&d_fileData, fileSize);
    cudaMemcpy(d_fileData, fileData.data(), fileSize, cudaMemcpyHostToDevice);

    int numTags = 0;
    int* d_numTags;
    cudaMalloc((void**)&d_numTags, sizeof(int));
    cudaMemcpy(d_numTags, &numTags, sizeof(int), cudaMemcpyHostToDevice);

    // ✅ Launch Kernel
    int numBlocks = (fileSize + BLOCK_SIZE - 1) / BLOCK_SIZE;
    extract_tags_kernel << <numBlocks, BLOCK_SIZE >> > (d_fileData, fileSize, nullptr, nullptr, numTags, d_numTags);
    cudaMemcpy(&numTags, d_numTags, sizeof(int), cudaMemcpyDeviceToHost);

    // ✅ Free memory
    cudaFree(d_fileData);
    cudaFree(d_numTags);
}

// ✅ Process text with CUDA
void process_text_with_cuda(std::string& text, std::vector<std::string>& tags, std::vector<int>& results) {
    int text_size = text.size();
    int num_tags = tags.size();

    char* d_text, * d_tags;
    int* d_results;
    cudaMalloc(&d_text, text_size * sizeof(char));
    cudaMalloc(&d_tags, num_tags * MAX_KEYWORD_LENGTH * sizeof(char));
    cudaMalloc(&d_results, num_tags * sizeof(int));

    cudaMemcpy(d_text, text.c_str(), text_size * sizeof(char), cudaMemcpyHostToDevice);

    std::vector<char> h_tags(num_tags * MAX_KEYWORD_LENGTH, 0);
    for (int i = 0; i < num_tags; i++) {
        strncpy(&h_tags[i * MAX_KEYWORD_LENGTH], tags[i].c_str(), MAX_KEYWORD_LENGTH);
    }

    cudaMemcpy(d_tags, h_tags.data(), num_tags * MAX_KEYWORD_LENGTH * sizeof(char), cudaMemcpyHostToDevice);
    cudaMemset(d_results, 0, num_tags * sizeof(int));

    int numBlocks = (text_size + BLOCK_SIZE - 1) / BLOCK_SIZE;
    extract_tags_kernel << <numBlocks, BLOCK_SIZE >> > (d_text, text_size, d_tags, nullptr, num_tags, d_results);

    results.resize(num_tags);
    cudaMemcpy(results.data(), d_results, num_tags * sizeof(int), cudaMemcpyDeviceToHost);

    cudaFree(d_text);
    cudaFree(d_tags);
    cudaFree(d_results);
}

//Called From Python
// ----- CUDA Kernel -----
__global__ void normalize_weather_data(WeatherPoint* data, size_t count) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) return;

    data[i].temperature /= 100.0f;
    data[i].humidity /= 100.0f;
    data[i].pressure /= 1000.0f;
}

// ----- CUDA Processing -----
void process_weather_with_cuda(std::vector<WeatherPoint>& points) {
    if (points.empty()) return;

    WeatherPoint* d_data;
    size_t size = points.size() * sizeof(WeatherPoint);

    cudaMalloc(&d_data, size);
    cudaMemcpy(d_data, points.data(), size, cudaMemcpyHostToDevice);

    int blockSize = 256;
    int gridSize = (points.size() + blockSize - 1) / blockSize;
    normalize_weather_data << <gridSize, blockSize >> > (d_data, points.size());

    cudaDeviceSynchronize();
    cudaMemcpy(points.data(), d_data, size, cudaMemcpyDeviceToHost);
    cudaFree(d_data);
}

// Helper to process a CSV line into float values
std::vector<float> parse_csv_line(const std::string& line) {
    std::vector<float> values;
    size_t start = 0;
    size_t end = line.find(',');

    while (end != std::string::npos) {
        values.push_back(std::stof(line.substr(start, end - start)));
        start = end + 1;
        end = line.find(',', start);
    }
    values.push_back(std::stof(line.substr(start)));

    return values;
}

__global__ void compute_trajectory(const WeatherPoint* input, TrajectoryPoint* output, int count) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count - 1) return;

    float dx = input[i + 1].temperature - input[i].temperature;
    float dy = input[i + 1].humidity - input[i].humidity;
    float dz = input[i + 1].pressure - input[i].pressure;

    float mag = sqrtf(dx * dx + dy * dy + dz * dz);

    int quadrant = 0;
    if (dx > 0 && dy > 0) quadrant = 1;
    else if (dx < 0 && dy > 0) quadrant = 2;
    else if (dx < 0 && dy < 0) quadrant = 3;
    else if (dx > 0 && dy < 0) quadrant = 4;

    output[i] = { dx, dy, dz, quadrant, mag };
}

void compute_weather_trajectory(const std::vector<WeatherPoint>& input, std::vector<TrajectoryPoint>& output) {
	if (input.size() < 2) return;

    int count = static_cast<int>(input.size());
    size_t input_size = count * sizeof(WeatherPoint);
    size_t output_size = (count - 1) * sizeof(TrajectoryPoint);

    WeatherPoint* d_input = nullptr;
    TrajectoryPoint* d_output = nullptr;

    // Allocate GPU memory
    cudaMalloc(&d_input, input_size);
    cudaMalloc(&d_output, output_size);

    // Copy input to device
    cudaMemcpy(d_input, input.data(), input_size, cudaMemcpyHostToDevice);

    // Launch kernel
    int blockSize = 256;
    int gridSize = (count - 1 + blockSize - 1) / blockSize;
    compute_trajectory << <gridSize, blockSize >> > (d_input, d_output, count);

    // Wait for GPU to finish
    cudaDeviceSynchronize();

    // Prepare output vector and copy back
    output.resize(count - 1);
    cudaMemcpy(output.data(), d_output, output_size, cudaMemcpyDeviceToHost);

    // Cleanup
    cudaFree(d_input);
    cudaFree(d_output);
}