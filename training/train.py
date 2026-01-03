from training.nlp_engine import NLPEngine
import os

def main():
    print("Starting training process...")
    nlp = NLPEngine()
    # Correct path relative to root where script takes place or absolute
    dataset_path = os.path.abspath('Resume/Resume.csv')
    print(f"Looking for dataset at: {dataset_path}")
    
    if os.path.exists(dataset_path):
        success = nlp.train(dataset_path)

        if success:
            print("Training completed successfully.")
        else:
            print("Training failed.")
    else:
        print(f"Dataset not found at {dataset_path}")

if __name__ == "__main__":
    main()
