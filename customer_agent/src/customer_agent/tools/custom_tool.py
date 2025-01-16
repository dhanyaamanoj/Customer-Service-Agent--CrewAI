from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type, Any, Optional
from pydantic import BaseModel, Field,validate_call
import pypdf
import pandas as pd


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
    




import requests
from typing import Optional, Any
from pydantic import BaseModel, Field
import json  # For saving the output as a JSON file


class UpdateMasterDataToolSchema(BaseModel):
    """Input schema for UpdateMasterDataTool."""
    request_filepath: str = Field(..., description="Full path to the CSV file containing policy service requests.")
    master_data_filepath: str = Field(..., description="Full path to the CSV file containing the master data.")


class UpdateMasterDataTool(BaseTool):
    """A tool for updating master data using policy service requests and master data CSV files.

    This tool inherits from BaseTool and uses the provided file paths to send a request to a FastAPI backend for updating the master data.
    The `args_schema` is set to UpdateMasterDataToolSchema which defines the required `request_filepath` and `master_data_filepath` parameters.

    Args:
        request_filepath (Optional[str]): Default path to the policy service requests CSV file. If provided,
            this becomes the default file path for the tool.
        master_data_filepath (Optional[str]): Default path to the master data CSV file. If provided,
            this becomes the default file path for the tool.
        **kwargs: Additional keyword arguments passed to BaseTool.

    Example:
        >>> tool = UpdateMasterDataTool(request_filepath="/path/to/policy_service_requests.csv", 
                                        master_data_filepath="/path/to/Insurance_Masterdata.csv")
        >>> result = tool.run()  # Updates master data using the provided CSV files
        >>> result = tool.run(request_filepath="/path/to/another_requests.csv", 
                            master_data_filepath="/path/to/another_masterdata.csv")  # Uses different files
    """
    name: str = "Update Master Data Tool"
    description: str = (
        "A tool that sends policy service requests and master data to a backend to update the master data. "
        "Provide 'request_filepath' and 'master_data_filepath' parameters with paths to the CSV files you want to use."
    )
    args_schema: Type[BaseModel] = UpdateMasterDataToolSchema
    request_filepath: Optional[str] = None
    master_data_filepath: Optional[str] = None

    def __init__(self, request_filepath: Optional[str] = None, master_data_filepath: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the UpdateMasterDataTool."""
        super().__init__(**kwargs)
        if request_filepath is not None:
            self.request_filepath = request_filepath
        if master_data_filepath is not None:
            self.master_data_filepath = master_data_filepath
        self.description = f"A tool for updating master data using files. Default files: {self.request_filepath}, {self.master_data_filepath}. You can provide alternative paths."

    def _run(self, **kwargs: Any) -> Any:
        request_filepath = kwargs.get("request_filepath", self.request_filepath)
        master_data_filepath = kwargs.get("master_data_filepath", self.master_data_filepath)

        if request_filepath is None or master_data_filepath is None:
            return {
                "error": "Both 'request_filepath' and 'master_data_filepath' must be provided either in the constructor or as arguments."
            }

        try:
            # Prepare the payload
            payload = {
                "request_filepath": request_filepath,
                "master_data_filepath": master_data_filepath
            }

            # Send the POST request to the FastAPI backend
            url = "http://127.0.0.1:8000/update_master_data/"
            response = requests.post(url, json=payload)

            # Handle the response from the FastAPI server
            if response.status_code == 200:
                output_data = response.json()  # Get the success response as a dictionary
                
                # Save the output in a new file (JSON format)
                output_filename = "update_result.json"  # Define the output file name
                with open(output_filename, "w") as output_file:
                    json.dump(output_data, output_file, indent=4)  # Save in JSON format
                
                return output_data  # Return the success response
            else:
                return {"error": f"Error: {response.status_code} - {response.json()}"}

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def _generate_description(self) -> None:
        """Generate the tool description based on the file paths."""
        self.description = f"A tool that can be used to update master data using the files: {self.request_filepath} and {self.master_data_filepath}."




# tool = PolicyDataUpdateTool(
#     request_filepath="path/to/policy_service_requests.csv",
#     masterdata_filepath="path/to/insurance_masterdata.csv"
# )

# result = tool._run()
# print(result) 
