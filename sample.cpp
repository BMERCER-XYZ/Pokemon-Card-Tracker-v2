#include <iostream>
#include <string>
#include <curl/curl.h>

// Callback to write the response into a std::string
size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

int main() {
    CURL* curl;
    CURLcode res;
    std::string readBuffer;

    curl = curl_easy_init();
    if(curl) {
        // URL of API (example: TCGPlayer card price endpoint)
        curl_easy_setopt(curl, CURLOPT_URL, "https://mpapi.tcgplayer.com/v2/product/610510/pricepoints");

        // Set callback to capture response
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);

        // Pass string to hold data
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

        // Perform request
        res = curl_easy_perform(curl);

        // Check for errors
        if(res != CURLE_OK) {
            std::cerr << "cURL error: " << curl_easy_strerror(res) << std::endl;
        } else {
            std::cout << "Response:\n" << readBuffer << std::endl;
        }

        // Cleanup
        curl_easy_cleanup(curl);
    }

    return 0;
}
