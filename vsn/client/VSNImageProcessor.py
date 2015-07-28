import cv2

from vsn.common.VSNUtility import ImageType


class VSNImageProcessor:
    def __init__(self, initial_frame):
        self.__background_image = cv2.cvtColor(initial_frame, cv2.COLOR_BGR2GRAY)
        self.__foreground_image = self.__background_image
        self.__difference_thresholded_image = self.__background_image
        self.__structing_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def get_image(self, image_type: ImageType):
        if image_type == ImageType.foreground:
            image = self.__foreground_image
        elif image_type == ImageType.background:
            image = self.__background_image
        else:
            image = self.__difference_thresholded_image

        return image

    def get_percentage_of_active_pixels_in_frame(self, frame):
        # process the frame
        self.__foreground_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # calculate the difference between current and background frame
        difference = cv2.absdiff(self.__background_image, self.__foreground_image)

        # process the difference
        # use median blur
        blurred = cv2.medianBlur(difference, 3)

        # do the thresholding
        display = cv2.compare(blurred, 6, cv2.CMP_GT)

        # erode and dilate
        eroded = cv2.erode(display, self.__structing_element)
        dilated = cv2.dilate(eroded, self.__structing_element)

        # store the difference image for further usage
        self.__difference_thresholded_image = dilated

        # count non zero elements
        nonzero_pixels = cv2.countNonZero(dilated)

        # calculate the number of non-zero pixels
        height, width = self.__foreground_image.shape
        percentage_of_nonzero_pixels = (nonzero_pixels * 100 / (height * width))

        # prepare data for background update
        mask_gt = cv2.compare(self.__background_image, self.__foreground_image, cv2.CMP_GT)
        mask_lt = cv2.compare(self.__background_image, self.__foreground_image, cv2.CMP_LT)

        # update the background
        self.__background_image += mask_lt >> 7
        self.__background_image -= mask_gt >> 7

        return percentage_of_nonzero_pixels
