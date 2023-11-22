#include <vector>
#include <stack>

using namespace std;

vector<int> collidingAsteroids(vector<int> asteroids) {
    stack<int> st;
    for (int ast : asteroids) {
        bool destroyed = false;
        while (!st.empty() && st.top() > 0 && ast < 0) {
            if (st.top() < -ast) {
                st.pop();
                continue;
            } else if (st.top() == -ast) {
                st.pop();
            }
            destroyed = true;
            break;
        }
        if (!destroyed) {
            st.push(ast);
        }
    }
    vector<int> result(st.size());
    for (int i = st.size() - 1; i >= 0; --i) {
        result[i] = st.top();
        st.pop();
    }
    return result;
}

/* 
Algo:
  - iterates through the asteroids vector.
  Conditions:
    - If the current asteroid (ast) is moving left (negative) and the top of the stack is moving right (positive), a collision occurs.
    - If the asteroid at the top of the stack is smaller, it's removed. If they are equal, both are destroyed.
    - If no collision happens (or after all collisions are resolved), the current asteroid is pushed onto the stack.  
    - Finally, the contents of the stack are transferred to a vector in reverse order */
