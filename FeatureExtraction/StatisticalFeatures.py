import numpy as np
from numba import jit
import timeit
import os
import cv2

class StatisticalFeatures():
    
    def __init__(self):
        self.featuresNumber = 56

    def getFeatures(self, image, showResults = False, black_background=True):
        features = []                                           # features vector
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        height, width = gray.shape
        features.append(height/width)

        # binarize image
        _, binary_img = cv2.threshold(gray, 128, 1, cv2.THRESH_BINARY)

        if black_background:
            binary_img = 1-binary_img
        else:
            gray = 255-gray

        fastfeatures, img_row_sum, img_col_sum = getFeaturesFast(binary_img, height, width)

        features.extend(fastfeatures)
        # Reduce horizontal and vertical histogram to 5 features each 
        chunks_count = 20
        # row_chunks = min(height, chunks_count)    
        # col_chunks = min(width, chunks_count)             
        
        img_row_sum_split = np.array_split(img_row_sum, chunks_count)                              # split into 5 chunks
        img_col_sum_split = np.array_split(img_col_sum, chunks_count)

        # append the average of the chunks to feature vector (for horizontal and vertical)
        for chunk in img_col_sum_split:                                                  
            if chunk.size != 0:
                features.append(np.average(chunk))
            else:
                features.append(0)
        for chunk in img_row_sum_split:
            if chunk.size != 0:
                features.append(np.average(chunk))
            else:
                features.append(0)
        
        return features
        
@jit(nopython=True)    
def getFeaturesFast(binary_img, height, width):
    fastfeatures = []
    black_pixels = 0                                                   # number of black pixels
    B1, B2, B3, B4 = 0, 0, 0, 0                                        # number of black pixels in each quarter
    cx = 0
    cy = 0
    # Calculate black pixels count, vertical, horizontal transitions count
    horizontal_transition_count = 0
    vertical_transition_count = 0
    VerticalLastPixel = np.ones(width)
    lastPixel = 1

    img_row_sum = np.zeros(height)                                     
    img_col_sum = np.zeros(width)  
    VerticalLastPixel = np.ones(width)
    lastPixel = 1

    img_row_sum = np.zeros(height)                                     
    img_col_sum = np.zeros(width)  

    for row in range(height):
        for col in range(width):
            if binary_img[row, col] == 0:
                black_pixels += 1
                if row < int(height/2): 
                    if col < int(width/2):
                        B1 += 1
                    else:
                        B2 += 1
                else:
                    if col < int(width/2):
                        B3 += 1
                    else:
                        B4 += 1 
                # Determine center of mass (of black ink)
                cx += col
                cy += row
                # Calculate horizontal and vertical histogram
                img_row_sum[row] += 1/width
                img_col_sum[col] += 1/height
            if(lastPixel != binary_img[row,col]):
                horizontal_transition_count += 1
            lastPixel = binary_img[row,col]
            if(VerticalLastPixel[col] != binary_img[row,col]):
                vertical_transition_count += 1
            VerticalLastPixel[col] = binary_img[row,col]

    pixels_count = height * width
    white_pixels = pixels_count - black_pixels                         # number of white pixels
    if white_pixels == 0:
        white_pixels =1
    fastfeatures.append(black_pixels/white_pixels)            
    # features.append(self.black_pixels / white_pixels)

    # append vertical and horizontal transitions count to feature vector
    fastfeatures.append(vertical_transition_count)
    fastfeatures.append(horizontal_transition_count)

    quarter_pixels = pixels_count / 4
    W1 = quarter_pixels - B1                                                     # number of white pixels in first quarter of image
    W2 = quarter_pixels - B2     
    W3 = quarter_pixels - B3
    W4 = quarter_pixels - B4 

    # avoid division by zero
    if W1 == 0:
        W1 =1 
    if W2 == 0:
        W2 =1 
    if W3 == 0:
        W3 =1 
    if W4 == 0:
        W4 =1 
    if B2 == 0:
        B2 =1 
    if B3 == 0:
        B3 =1 
    if B4 == 0:
        B4 =1 

    fastfeatures.extend([B1/W1, B2/W2, B3/W3, B4/W4, B1/B2, B1/B3, B1/B4, B2/B3, B2/B4, B3/B4])
    
    # append center of mass to feature vector
    if black_pixels == 0:
        black_pixels =1
    centerX = int(cx / black_pixels)
    centerY = int(cy / black_pixels)

    fastfeatures.extend([centerX/width, centerY/height])

    # features.extend(np.average(img_row_sum_split, axis=1))
    # features.extend(np.average(img_col_sum_split, axis=1))

    # for _ in range((chunks_count-row_chunks) + (chunks_count-col_chunks)):
    #     features.append(0)

    return fastfeatures , img_row_sum, img_col_sum

    
if __name__ == "__main__":    
    statFeatures = StatisticalFeatures()

    img = cv2.imread("../Dataset/capr2.png")
    start_time = timeit.default_timer()     # start timer
    features = statFeatures.getFeatures(img, False)
    print (timeit.default_timer() - start_time)
    print(features)

    #cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    #cv2.imshow('image', img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()