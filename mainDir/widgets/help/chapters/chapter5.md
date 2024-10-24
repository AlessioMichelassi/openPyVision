# Chapter 5 - More Input

In the previous chapter, we discussed and wrote a lot of code to build the foundation of a video mixer. In Chapter 5, we focus on consolidating and organizing this code into a more definitive structure, integrating new features to improve the management of the program's data and resources.

image::https://github.com/AlessioMichelassi/openPyVision*013/blob/master/wiki/imgs/cap5*0_theMainFolder.png[scaledwidth="50%"]

The code structure we've built is organized into several directories, similar to those in the OpenPyVision Mixer project. Within the main directory, you will find folders dedicated to inputs, which contain the generators we have used so far, the synchObject, and the extended base class. There is a dedicated folder for the mixBus, which also includes the management of stingers—the transition animations used to switch from one scene to another. The output folder contains the class for OpenGL visualization, representing the final result of the video mixing and manipulation operations.

One of the new features introduced in this chapter is the `DataManager` class, which is responsible for managing the default locations of folders containing resources such as stingers and still images. This class is designed to automatically load and save this information, ensuring that the program doesn't crash if the folders are not found. The `DataManager` leverages the functionality built in Chapter 4 to load stingers and still images, and then passes these elements to the `mixBus` for processing.

The operation of the `DataManager` is quite straightforward: upon startup, the class attempts to load the saved paths from a JSON file. If the file does not exist or is corrupted, a new file is created with default values. The `DataManager` also handles the loading of stingers through a separate thread, displaying a progress widget during loading to inform the user of the operation's status. If something goes wrong, such as a path not being found, the `DataManager` signals the error, keeping the program stable and informing the user.

