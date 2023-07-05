import cv2
import numpy as np

# Znajdź szerokość trasy w danym punkcie dla zbinaryzowanej mapy drogowej
def getRoadWidth(road_map_bin, coordinates):
    
    R = 1
    segments_count = 0
    first_segment_found_iteration = -1 # moment "pojawienia się" pierwszego segmentu
    current_iteration = 0
    
    # część wspólna brzegów i okręgu, dopóki nie istnieją co najmniej 2 segmenty
    while segments_count < 2:

        # pusty obrazek o analogicznych wymiarach, co mapa
        road_map_frame = np.zeros(road_map_bin.shape, np.uint8)

        # rysowanie okręgu o promieniu R
        cv2.circle(road_map_frame, coordinates, R, (255,255,255), -1 );

        # część wspólna z brzegami przy drodzę
        road_map_circle_XOR = cv2.bitwise_xor(road_map_bin, road_map_frame)
        intersection = cv2.bitwise_and(road_map_circle_XOR, road_map_frame)

        # segmentacja części wspólnej i zapisanie ilość znalezionych segmentów
        contours, hierarchy = cv2.findContours(intersection[:,:,0], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # zliczanie znalezionych konturów
        segments_count = len(contours)

        # sprawdzanie, czy pojawił się pierwszy kontur
        if segments_count == 1 and first_segment_found_iteration == -1:
            first_segment_found_iteration = current_iteration

        current_iteration = current_iteration + 1
        R = R + 1

    # Sprawdzanie, czy oba segmenty zostały znalezione jednocześnie
    if first_segment_found_iteration == -1:
        first_segment_found_iteration = current_iteration

    # Policzenie szerokości trasy w danym koordynacie
    return (current_iteration - 1)*2 - (current_iteration - first_segment_found_iteration - 1)   

# wczytanie mapy
road_map = cv2.imread('road_map_512x512.png', cv2.COLOR_BGR2GRAY)

# # binaryzacja mapy
_, road_map_bin = cv2.threshold( road_map, 126, 255, cv2.THRESH_BINARY )

# wczytanie współrzędnych wskazujących punkty trasy
loaded_input = np.loadtxt("img.csv", delimiter=' ', dtype=str)
all_road_coordinates = []
NX, NY = loaded_input.shape
for x in range(NX):
    for y in range(NY):
        if loaded_input[x,y] == '1':
            all_road_coordinates.append([x,y])

# output w takiej samej formie, co input, ale z wartościami będącymi szerokością trasy
output = np.zeros((512,512), np.uint8)
for coordinates in all_road_coordinates:
    X, Y = coordinates
    output[X,Y] = getRoadWidth(road_map_bin,coordinates)
