# examples/breast_cancer_demo.py

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score

from cause import CCE_ANM_Model


def main():
    data = load_breast_cancer()
    X = data.data
    y = data.target
    feature_names = list(data.feature_names)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    clf = AdaBoostClassifier(
        n_estimators=100, learning_rate=1.0, random_state=42
    )
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Black-box accuracy: {acc:.3f}")

    f_bb = lambda Xin: clf.predict_proba(Xin)

    model = CCE_ANM_Model(
        lambda_=2.0, mu=50.0, K_cce=30, K_cai=120, n_restarts=4
    )

    import time
    start = time.time()
    model.fit(X_train, f_bb)
    print("Total edges:", model._adj.sum())
    print(f"\nTotal fit time: {time.time() - start:.2f} seconds")

    # Example explanation for one test instance
    x_obs = X_test[0]
    y_foil = 1.0  # target class
    result = model.explain(
        x_obs, y_foil, feature_names=feature_names, verbose=True
    )
    result.summary()


if __name__ == "__main__":
    main()