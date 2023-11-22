//PCO
struct TrieNode {
    unordered_map<char, TrieNode*> children;
    int count;
    TrieNode() : count(0) {}
};
void insert(TrieNode* root, const string& str) {
    TrieNode* node = root;
    for (char ch : str) {
        if (!node->children.count(ch)) {
            node->children[ch] = new TrieNode();
        }
        node = node->children[ch];
        node->count++;
    }
}
string findPrefix(TrieNode* root, const string& str) {
    string prefix;
    TrieNode* node = root;
    for (char ch : str) {
        prefix += ch;
        node = node->children[ch];
        if (node->count == 1) {
            break;
        }
    }
    return prefix;
}
vector<string> shortestUniquePrefixes(vector<string> strings) {
    TrieNode* root = new TrieNode();
    // Build the Trie
    for (const string& str : strings) {
        insert(root, str);
    }
    // shortest unique prefixes
    vector<string> prefixes;
    for (const string& str : strings) {
        prefixes.push_back(findPrefix(root, str));
    }
    return prefixes;
}
