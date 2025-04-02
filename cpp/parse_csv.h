#pragma once
#include "../cpp/tag_dir.h"


// Function declarations
std::vector<WeatherPoint> parse_csv(const std::string& filepath);
std::vector<std::string> find_all_csv_files(const std::string& root_dir);
std::vector<WeatherPoint> parse_csv(const std::string& filepath);
std::vector<std::string> find_all_csv_files(const std::string& root_dir);
void write_binary(const std::string& output_path, const std::vector<WeatherPoint>& points);
extern "C" __declspec(dllexport) void __stdcall package_csvs_to_bin(const char* input_dir, const char* output_file);
