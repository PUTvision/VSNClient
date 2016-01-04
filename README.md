## cam_network

Control software (written in Python) for a network of smart cameras based on RaspberryPi boards.

## Acknowledgment

This code is used in the project entitled:

*"NEW CONCEPT OF THE NETWORK OF SMART CAMERAS WITH ENHANCED AUTONOMY FOR AUTOMATIC SURVEILLANCE SYSTEM"*

More information about the project can be found: http://www.vision.put.poznan.pl/?page_id=237

## Project in a nutshell (description)

The aim of the provided code is to test the algorithms for controlling the network of smart cameras.

Each camera node is based on RaspberryPi board which is handling all the processing. Based on the motion detected on the observed scene, the camera is changing how frequently it captures the image and do the processing. In addition to that the current activity level is propagated to neighbouring nodes (through central server) which also influence how active each camera is.

Such solution enables to put most of the camera in the system into low power mode, and do the image processing relatively infrequently. As a result the whole system is saving power which can enable it to operate on battery. On the other hand thanks to the propagation of information about motion between cameras no important information is lost.

## Languages and tools used
Project is written in Python 3.4 and uses following libraries (+ all the prequisitions for those):
* opencv - for image acquisition processing tasks,
* pyqtgraph - for plotting,
* picamera - for capturing images (optional),
* pyalpm - for updating client software.

## Running the code
Copy the repository to RaspberryPi (git clone) board and install all the libraries required. If you already have the repository, do just git pull. Change the hostname of the RPi to one of the following: picam0n (where n is number) or switch hostname based ids off in config file.

Start the server on the central node, and then start client software on each RPi.

## Modules description
Connectivity:
* client
* server
* multicast

Common:
* decorators
* version
* VSNPacket
* VSNUtility

Server:
* VSNServer
* VSNGraph
* VSNCamera
* VSNCameras

Client:
* VSNClient
* VSNActivityController
* VSNImageProcessor
* VSNCamera
* VSNReactor
* VSNUpdater

## Scripts description
* VSNServer - run server software,
* VSNClientCV - run client software using OpenCV for capturing,
* VSNClientPiCamera - run client software using picamera for capturing,
* VSNHistoryPlotter - view saved plots,
* VSNUpdater - update software.

## License

MIT
