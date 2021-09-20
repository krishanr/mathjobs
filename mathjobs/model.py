from sklearn import preprocessing
import numpy as np
from sklearn.linear_model import LinearRegression
import sklearn
from mathjob_ovtime import find_trends

def get_predictions(X, y):
    """
        X is pandas series containing publication counts for a list of years.
        y is a list of job counts for a list of years.
        Note that X and y have the same length, with 
        X.iloc[5] and y[5] the repsective counts for year 6.
        
        A one variable linear regression model is built to predict the y from X,
        and then the preditions are returned.
    """
    # Use the previous year from arxiv publications.
    data = np.array([X.id.to_list(),y])

    scaler = preprocessing.StandardScaler().fit(data.T)
    data = scaler.transform(data.T).T

    lr = LinearRegression().fit( data[0].reshape(-1,1), data[1])

    predicted_data = np.array([list(data[0]),list(lr.predict(data[0].reshape(-1,1)))])
    predicted_data = scaler.inverse_transform(predicted_data.T).T

    return predicted_data

