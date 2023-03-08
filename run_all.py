from calibrateCameraByChessboard import calibrate
from generatePOM import generate_POM
from perceptionHandler import perceptionHandler
from generateAnnotation import annotate

if __name__ == '__main__':
    calibrate()
    generate_POM()
    perceptionHandler()
    annotate()