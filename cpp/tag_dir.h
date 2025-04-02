#define _CRT_SECURE_NO_WARNINGS 

#ifndef DIR_TAG_H
#define DIR_TAG_H

#include "../cuda/kernel.cuh"
#include <windows.h>
#include <filesystem>

namespace fs = std::filesystem; 

// Function declarations
void get_list_directory_full();
__host__ json process_text_files(const std::string& filepath, const std::unordered_map<std::string, std::vector<std::string>>& tags);

std::string preprocess_docx_text(const std::string& text);
__host__ json build_json_summary(const std::vector<int>& counts, const std::vector<std::vector<int>>& positions, const std::vector<std::string>& tags);

json build_json_summary(const std::vector<int>& counts, const std::vector<std::vector<int>>& positions, const std::vector<std::string>& tags);
std::string preprocess_docx_text(const std::string& text);
void process_directory_code(const std::string& directory, const std::string& tag_file, const std::string& code_file);

#endif // DIR_TAG_H
