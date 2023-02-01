import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

X, y = load_digits(n_class=12, return_X_y=True)
rnd_state = 5
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=rnd_state)
mlp = MLPClassifier()
mlp.fit(X_train, y_train)
print(f'Accuracy: {mlp.score(X_test, y_test) * 100:.2f}%')
nrows = 2
ncols = 5
figure = plt.figure(figsize = (15, 7))
axis = [figure.add_subplot(nrows, ncols, ncols * x + y + 1)
      for x in range(nrows) for y in range(ncols)]
plt.suptitle('Prediction Results', size = 30)
test_set = np.random.choice(X_test.shape[0],10)
print("Prediction Results:")
for index, test_index in enumerate(test_set):
    d_matrix = X_test[test_index]
    pred_num = mlp.predict([d_matrix])[0]
    print(f'{index}) X_test[{test_index}] = {pred_num}')
    ax = axis[index]
    ax.matshow(d_matrix.reshape(8, 8), cmap = 'gray')
    ax.set_xlabel(f'X_test[{test_index}] = {pred_num}', color = 'r', size = 16)
    ax.set_xticks([])
    ax.set_yticks([])
	
"""Output:

Accuracy: 96.89% | Prediction Results:
		0) X_test[234] = 3
		1) X_test[429] = 7
		2) X_test[325] = 6
		3) X_test[213] = 9
		4) X_test[412] = 3
		5) X_test[429] = 7
		6) X_test[420] = 6
		7) X_test[209] = 7
		8) X_test[389] = 9
		9) X_test[75] = 0
	
."""
