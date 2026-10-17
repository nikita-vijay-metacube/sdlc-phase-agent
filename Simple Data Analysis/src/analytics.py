import os
import re
import pandas as pd
import matplotlib.pyplot as plt

class RequestAnalytics:
    def __init__(self, filepath: str = "data/requests.json"):
        self.filepath = filepath

    def load_dataframe(self) -> pd.DataFrame:
        """Loads requests from JSON into a pandas DataFrame."""
        if not os.path.exists(self.filepath):
            return pd.DataFrame(columns=["id", "description", "client", "project", "timestamp"])
        try:
            df = pd.read_json(self.filepath)
            if df.empty:
                return pd.DataFrame(columns=["id", "description", "client", "project", "timestamp"])
            return df
        except (ValueError, Exception):
            return pd.DataFrame(columns=["id", "description", "client", "project", "timestamp"])

    def calculate_stats(self) -> dict:
        """Calculates total requests, average length, and keyword frequencies."""
        df = self.load_dataframe()
        if df.empty:
            return {
                "total_requests": 0,
                "avg_length": 0.0,
                "keyword_counts": {}
            }
        
        total_requests = len(df)
        avg_length = df["description"].str.len().mean()

        # Track common keywords across descriptions
        target_keywords = ["login", "database", "test", "payment", "user", "system", "report", "dashboard"]
        all_text = " ".join(df["description"].astype(str)).lower()
        
        keyword_counts = {}
        for kw in target_keywords:
            count = len(re.findall(rf"\b{kw}\b", all_text))
            if count > 0:
                keyword_counts[kw] = count

        return {
            "total_requests": total_requests,
            "avg_length": round(avg_length, 2),
            "keyword_counts": keyword_counts
        }

    def generate_chart(self, output_path: str = "data/analytics_chart.png") -> str:
        """Generates a bar chart of keyword frequencies and saves it as a PNG."""
        stats = self.calculate_stats()
        keyword_counts = stats["keyword_counts"]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        plt.figure(figsize=(8, 5))
        
        if not keyword_counts:
            plt.bar(["No Data"], [0], color="#cccccc")
            plt.title("Feature Request Keyword Frequency (No Data)")
        else:
            keywords = list(keyword_counts.keys())
            counts = list(keyword_counts.values())
            plt.bar(keywords, counts, color="#4A90E2", edgecolor="black")
            plt.title("Feature Request Keyword Frequency")
            plt.xlabel("Keywords")
            plt.ylabel("Frequency")
            plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return output_path