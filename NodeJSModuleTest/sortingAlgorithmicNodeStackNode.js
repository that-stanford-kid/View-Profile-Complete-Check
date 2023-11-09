// algos
function bubbleSort(arr, comparator) {
    let n = arr.length;
    let swapped;
    do {
        swapped = false;
        for (let i = 0; i < n - 1; i++) {
            if (comparator(arr[i], arr[i + 1]) > 0) {
                [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                swapped = true;
            }
        }
        n--; // Decrease n as the largest element 
    } while (swapped);
    return arr;
}

function cocktailSort(arr, comparator) {
    let start = 0;
    let end = arr.length - 1;
    let swapped;
    do {
        swapped = false;
        for (let i = start; i < end; i++) {
            if (comparator(arr[i], arr[i + 1]) > 0) {
                [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                swapped = true;
            }
        }
        if (!swapped) break;
        swapped = false;
        end--;
        for (let i = end; i > start; i--) {
            if (comparator(arr[i - 1], arr[i]) > 0) {
                [arr[i], arr[i - 1]] = [arr[i - 1], arr[i]];
                swapped = true;
            }
        }
        start++;
    } while (swapped && start < end);
    return arr;
}

function shakerSort(arr, comparator) {
    let isSwapped;
    let start = 0;
    let end = arr.length;
    do {
        isSwapped = false;
        for (let i = start; i < end - 1; ++i) {
            if (comparator(arr[i], arr[i + 1]) > 0) {
                [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                isSwapped = true;
            }
        }
        if (!isSwapped) break;
        isSwapped = false;
        end--;
        for (let i = end - 1; i >= start; --i) {
            if (comparator(arr[i], arr[i + 1]) > 0) {
                [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                isSwapped = true;
            }
        }
        start++;
    } while (isSwapped);
    return arr;
}

// Define default comparator
function defaultComparator(a, b) {
    return a - b;
}

// Assign description properties to the sorting functions
function setDescription(fn, description) {
    Object.defineProperty(fn, 'description', {
        value: description,
        writable: false
    });
}

// Setting for each sorting function
setDescription(bubbleSort, 'Optimized Bubble Sort algorithm.');
setDescription(cocktailSort, 'Optimized Cocktail Shaker Sort algorithm.');
setDescription(shakerSort, 'Optimized Shaker Sort algorithm.');

module.exports = {
    bubbleSort,
    cocktailSort,
    shakerSort,
    defaultComparator
};

// This section would be for the execution
if (require.main === module) {
    main(process.argv.slice(2));
}
