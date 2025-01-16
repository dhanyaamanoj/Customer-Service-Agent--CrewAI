from pydantic import BaseModel, Field
from typing import List, Dict, Type, Optional, Any
import pandas as pd

# Input schema for reading the policy service requests CSV file
class RequestCSVReaderInput(BaseModel):
    filepath: str = Field(..., description="Path to the `policy_service_requests.csv` file.")

# Tool for reading requests from the CSV
class RequestCSVReaderTool:
    name: str = "Request CSV Reader Tool"
    description: str = "Read requests from the CSV file and extract required fields."
    
    def run(self, filepath: str) -> List[Dict]:
        try:
            # Read the CSV file
            df = pd.read_csv(filepath)

            # Extract the required columns
            requests = []
            for _, row in df.iterrows():
                request = {
                    "request_id": row["Request_ID"],
                    "customer_id": row["Customer_ID"],
                    "request_type": row["Request_Type"],
                    "new_details": row["Changes"],  # Correct column name for new details
                }
                requests.append(request)

            return requests

        except Exception as e:
            return f"An error occurred while reading the requests CSV: {str(e)}"

# Input schema for updating the master data CSV file
class MasterDataUpdaterInput(BaseModel):
    filepath: str = Field(..., description="Path to the `insurance_masterdata.csv` file.")
    updates: List[Dict] = Field(..., description="List of updates from the Reasoner.")

# Tool for updating the master data CSV based on the Reasoner output
class MasterDataUpdaterTool:
    name: str = "Master Data Updater Tool"
    description: str = "Apply updates to the master data CSV based on the Reasoner output."
    
    def run(self, filepath: str, updates: List[Dict]) -> str:
        try:
            # Load the master data CSV
            df = pd.read_csv(filepath)

            # Strip extra spaces from column names and values
            df.columns = df.columns.str.strip()

            # Apply updates
            for update in updates:
                customer_id = update["customer_id"]
                request_type = update["request_type"]
                new_details = update["new_details"]

                # Map request types to corresponding columns
                if request_type == "Update Address":
                    column = "Address"
                    new_value = new_details.split(":")[-1].strip()  # Extract address from the format "New Address: xyz"
                elif request_type == "Update Policy type":
                    column = "Policy Type"
                    new_value = new_details.split(":")[-1].strip()  # Extract policy type from the format "New type: xyz"
                elif request_type == "Name change":
                    column = "Name"
                    new_value = new_details.split(":")[-1].strip()  # Extract name from the format "New Name: xyz"
                else:
                    return f"Error: Request type `{request_type}` is not supported."

                if column not in df.columns:
                    return f"Error: Column `{column}` not found in the dataset."
                
                # Ensure customer_id is treated as a string to avoid type mismatch
                match = df["Customer_ID"].astype(str) == str(customer_id)
                if not any(match):
                    return f"Error: Customer ID `{customer_id}` not found."

                # Update the master data
                df.loc[match, column] = new_value

            # Save changes to the file
            df.to_csv(filepath, index=False)

            return f"Successfully updated {len(updates)} records."

        except Exception as e:
            return f"An error occurred while updating the master data: {str(e)}"

# Combined tool class that includes both RequestCSVReaderTool and MasterDataUpdaterTool
class RequestMasterDataUpdaterTool(BaseModel):
    name: str = "Request Master Data Updater Tool"
    description: str = "A combined tool that reads requests from the request CSV and applies updates to the master data CSV."
    request_filepath: str = Field(..., description="File path to the `policy_service_requests.csv` file.")
    master_data_filepath: str = Field(..., description="File path to the `insurance_masterdata.csv` file.")

    def run(self) -> str:
        """Run the tool to read the request CSV and update the master data CSV."""
        if not self.request_filepath or not self.master_data_filepath:
            return "Error: Missing required parameters (request_filepath or master_data_filepath). Please provide both."

        try:
            # Step 1: Read request CSV
            csv_reader_tool = RequestCSVReaderTool()
            requests = csv_reader_tool.run(filepath=self.request_filepath)

            # Step 2: Apply updates to master data CSV
            master_data_updater_tool = MasterDataUpdaterTool()
            update_result = master_data_updater_tool.run(filepath=self.master_data_filepath, updates=requests)

            return update_result

        except Exception as e:
            return f"An error occurred: {str(e)}"

# Example of testing the combined tool with external file paths
def test_request_master_data_updater_tool():
    request_filepath = r"C:\Users\DHANYA MANOJ\OneDrive\Desktop\Final_Crew\customer_agent\knowledge\policy_service_requests.csv"
    master_data_filepath = r"C:\Users\DHANYA MANOJ\OneDrive\Desktop\Final_Crew\customer_agent\knowledge\Insurance_Masterdata.csv"

    tool = RequestMasterDataUpdaterTool(request_filepath=request_filepath, master_data_filepath=master_data_filepath)
    result = tool.run()
    print("Result of Update:")
    print(result)

# Run the test
if __name__ == "__main__":
    test_request_master_data_updater_tool()
