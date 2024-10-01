import pandas as pd
import joblib
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import os

def load_model(model_path):
    model = joblib.load(model_path)
    return model

def preprocess_data(data, cat_features, num_features):
    numeric_transformer = StandardScaler()
    oh_transformer = OneHotEncoder()
    preprocessor = ColumnTransformer(
        [
            ("OneHotEncoder", oh_transformer, cat_features),
            ("StandardScaler", numeric_transformer, num_features)
        ]
    )
    processed_data = preprocessor.fit_transform(data)
    return processed_data

def predict_yield(model, data):
    predictions = model.predict(data)
    return predictions

if __name__ == "__main__":
    
    base_path = "/home/satyukt/Sarthak/Escorts_Kubota_task" #Change base directory path.
    model_path = "/home/satyukt/Desktop/tasker/models/RandomForestRegressor_model.pkl" #Change model path as per need, I am uisng RandomForestRegressor.
    test_data = pd.read_csv("/home/satyukt/Desktop/tasker/csv/tester.csv") #Change testing file path as per need.
    
    
    out_path = f"{base_path}/models_prediction"
    os.makedirs(out_path, exist_ok=True)
    
    model_name = (model_path.split(".")[0]).split("/")[-1]
    
    cat_features = ['Season']
    num_features = ["total_Rainfall",
                    "Wind Speed",
                    "Temperature (°C)",
                    "NDVI",	"LST",
                    "rsm",
                    "Relative Humidity"
                    ]
    
    processed_data = preprocess_data(test_data, cat_features, num_features)
    model = load_model(model_path)
    predictions = predict_yield(model, processed_data)
    pred_column = f"Yield (Tonnes/Hectare)_{model_name}"
    prediction_df = pd.DataFrame(predictions, columns=[pred_column])
    final_result = pd.concat([test_data.reset_index(drop=True), prediction_df], axis=1)
    final_result.to_csv(f"{out_path}/predictions.csv", index=False)
    print(f"Prediction saved a loc: {out_path}")
    