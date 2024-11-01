#retrive images and dates

def image_retriever(path):
    import os
    import re
    from datetime import datetime
    from PIL import Image

    # Specify the folder containing TIFF images
    folder_path = path

    # Initialize a list to store [date as string, image data]
    image_data_list = []

    # Define a regular expression pattern to extract dates from filenames
    # Modify the pattern based on the date format in filenames
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")  # Example for format YYYY-MM-DD

    # Iterate through files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".tif") or file_name.endswith(".tiff"):
            # Extract date from filename using the defined pattern
            date_match = date_pattern.search(file_name)
            if date_match:
                date_str = date_match.group()  # Get the date string
                try:
                    # Convert the date string to a datetime object (optional, you can skip this if you don't need it)
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"Date format not recognized in filename: {file_name}")
                    continue
                
                # Load the TIFF image data
                file_path = os.path.join(folder_path, file_name)
                image_data_list.append([date_str, file_path]) 
               

    return image_data_list

# Example usage
# image_data = image_retriever("path/to/your/tiff/files")