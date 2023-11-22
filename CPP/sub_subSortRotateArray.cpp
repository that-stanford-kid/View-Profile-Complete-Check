#include <iostream>
#include <vector>
#include <unordered_map>
// PCO
using namespace std;

bool zeroSumSubarray(const vector<int>& nums) {
    unordered_map<int, int> sumMap;
    int cumSum = 0;
    for (int num : nums) {
        cumSum += num;
        // Check if cumSum is zero or already exists in sumMap
        if (cumSum == 0 || sumMap.find(cumSum) != sumMap.end()) {
            return true;
        }
        sumMap[cumSum]++;
    }
    return false;
}
int main() {
    // Example
    vector<int> nums = {1, 2, -3, 3, 4, -4};
    bool result = zeroSumSubarray(nums);
    cout << (result ? "True" : "False") << endl;
    return 0;
}
