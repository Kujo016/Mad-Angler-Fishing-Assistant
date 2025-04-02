#ifndef KERNEL_CUH
#define KERNEL_CUH

#include <cuda_runtime.h>
#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <cctype>
#include <regex>
#include <codecvt>
#include <locale>
#include <nlohmann/json.hpp>
#include <unordered_set>
#include <future>
#include <cstdlib>






#define MAX_SENTENCES 1024
#define MAX_WORDS 1024
#define MAX_SUMMARY_SENTENCES 5
#define MAX_LINE_LENGTH 1024
#define MAX_KEYWORD_LENGTH 32
#define MAX_KEYWORDS 100
#define BLOCK_SIZE 256  // Threads per block

#define DLLEXPORT extern "C" __declspec(dllexport)


using json = nlohmann::json;




// ----- Weather Data Struct -----
struct WeatherPoint {
    float temperature;
    float humidity;
    float pressure;
};

struct TrajectoryPoint {
    float dx;
    float dy;
    float dz;
    int quadrant;
    float magnitude;
};


// ✅ CUDA kernels for processing
__host__ void load_tags_cuda(const std::string& filepath, std::unordered_set<std::string>& tags);
__device__ bool contains(const char* line, const char* keyword);
__global__ void tag_text_lines(char* lines, char* keywords, int* results, int num_lines, int num_keywords, int max_line_length);
__host__ json process_text_files(const std::string& filepath, const std::unordered_map<std::string, std::vector<std::string>>& tags);
__global__ void extract_tags_kernel(char* fileData, int fileSize, char* tags, int* tagOffsets, int numTags, int* results);


// ✅ CUDA wrapper functions
void process_text_with_cuda(std::string& text, std::vector<std::string>& tags, std::vector<int>& results);
std::string removeInvalidUtf8(const std::string& input);
std::vector<std::string> read_txt(const std::string& filepath);

//Parsing Funtions
__global__ void normalize_weather_data(WeatherPoint* data, size_t count);
void process_weather_with_cuda(std::vector<WeatherPoint>& points);
std::vector<float> parse_csv_line(const std::string& line);

//Trajecctory
__global__ void compute_trajectory(const WeatherPoint* input, TrajectoryPoint* output, int count);
void compute_weather_trajectory(const std::vector<WeatherPoint>& input, std::vector<TrajectoryPoint>& output);



#endif // KERNEL_CUH





