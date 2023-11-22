class BinaryTree {
    constructor(value) {
        this.value = value;
        this.left = null;
        this.right = null;
    }
}
function mergeBinaryTrees(tree1, tree2) {
    if (!tree1 && !tree2) {
        return null;
    }
    if (!tree1) {
        return tree2;
    }
    if (!tree2) {
        return tree1;
    }
    tree1.value += tree2.value;
    tree1.left = mergeBinaryTrees(tree1.left, tree2.left);
    tree1.right = mergeBinaryTrees(tree1.right, tree2.right);

    return tree1;
}
exports.BinaryTree = BinaryTree;
exports.mergeBinaryTrees = mergeBinaryTrees; 
// if t1 and t2 are null -> null else -> swap t -> recurse -> merge -> child of t1,t2
