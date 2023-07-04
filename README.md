# VRP Solver Using Google Maps

This repository uses or-tools to solve the Vehicle Routing Problem (VRP) problem for a given set of vehicles and nodes to visit. It uses the Google Maps API to manage the locations of interest and represent the routes for each vehicle.

## Author

Francisco Javier Gañán

Affiliation: GRVC Robotics Lab, University of Seville

Mail: fjganan14@gmail.com

## Installation

1. Untar the project in the dersired parent folder of the repository.
    ```
    cd /folder_containing_the_tar_file
    ```

    ```
    tar -xf VRP.tar.xz --directory /parent_folder_of_the_repo

    ```

2. Create a conda environment.

    ```
    conda env create -f environment.yml

    ```
3. Install gmplot using pip.

    ```
    pip install gmplot
    ```

## Usage

1. Activate conda environment.

    ```
    cd /parent_folder_of_the_repo/VRP
    ```

    ```
    conda activate vrp
    ```

2. Substitute YOUR_API_KEY for your Google Maps API_KEY in the *internal.yaml* file and in the follwing part of the *index.html* file:

    ```html
    <script
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY=getMap" async defer>
    </script>
    ```

3. Launch the app.

    ```
    python3 main.py
    ```

4. The app has the following functionalities:

    -  You can add the addresses in the coordinates or written direction formats with the **Add Address** button. The same for the **Depot** button.

    - You can load the problem and solver configurations from given files (defined in the *cfg* folder). Use the buttons **Load Problem Definition from File** and **Load Solver Configuration**, respectively.

    - You can configure and modify the problem definition: 
        - The directions, by adding new ones by clicking in the map desired location, or deleting them hovering the mouse over the markers and clicking the delete option.
        - The problem definition within the problem definition section.

    - You can also generate routes, save the nodes and current routes, and select the travel mode with the corresponding buttons. Saved yaml files will be stores in the *output* folder of the project.

## Notes for the continuer

    This is a project under development, and not structured and documented the best way. I am probably missing something, so do not hesitate to contact me if you do need some help to understand anything or to continue with the work!

