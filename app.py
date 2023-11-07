import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans, KMeans
from sewar.full_ref import mse, msssim, psnr, sam, scc
import pandas as pd
import os
import streamlit as st
st.set_page_config(layout="wide")

def count_colours(src):
    pixels = src.reshape(-1, 3)

    # Convert the pixel array to a list of tuples
    pixel_list = [tuple(pixel) for pixel in pixels]

    # Use set() to get unique colors
    unique_colors = set(pixel_list)

    return len(unique_colors)

def quant_image(rgb_img, clusters):
    reshaped_image = np.reshape(rgb_img, ((rgb_img.shape[0] * rgb_img.shape[1]), 3))

    #model = MiniBatchKMeans(n_clusters=clusters, batch_size=2304)
    model = KMeans(n_clusters=clusters)
    target = model.fit_predict(reshaped_image)
    color_space = model.cluster_centers_

    output_image = np.reshape(color_space.astype("uint8")[target], (rgb_img.shape[0], rgb_img.shape[1], 3))
    con_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
    return count_colours(output_image), output_image

col1, col2, col3 = st.columns(3)
clusters = 2

with col1:
    img = st.file_uploader("Upload a file",type=['png', 'jpg','jpeg'])

with col2:
    st.markdown("**Image Metadata**")
    if img is not None:
        # Convert the file to an opencv image.
        file_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        total_colors = count_colours(opencv_image)
    
        st.markdown("Height x Width Resolution: {a} x {b}".format(a=opencv_image.shape[0],b=opencv_image.shape[1]))
        st.markdown("Total Colors : {}".format(total_colors))
        # Now do something with the image! For example, let's display it:
        st.markdown("*Image Preview*.")
        st.image(opencv_image, channels="BGR")
        clusters = st.slider(label="Select the Number of Clusters (By Default 2)",min_value=2,max_value=1000)
        colors , con_img = quant_image(opencv_image,clusters)

        
with col3:
    st.markdown("**Output Here**")
    try:
        if con_img is not None:
            st.image(con_img)
            new_row = {
            'psnr':psnr(opencv_image, con_img),
            'sam':sam(opencv_image, con_img),
            'scc':scc(opencv_image, con_img)
            }
            st.write("Calculated Metrics")
            st.write("MSE (Less=Better): {:.2f}".format(mse(opencv_image, con_img)))
            st.write("[MSSSIM](https://ieeexplore.ieee.org/abstract/document/1292216/) (High=Better): ",str(msssim(opencv_image, con_img))[1:5])
            st.write("[PSNR](https://ieeexplore.ieee.org/abstract/document/1284395/) (Less=Better): {:.2f}".format(psnr(opencv_image, con_img)))
            st.write("[SAM](https://ntrs.nasa.gov/search.jsp?R=19940012238) (Less=Better): {:.2f}".format(sam(opencv_image, con_img)))
            st.write("[SCC](https://www.tandfonline.com/doi/abs/10.1080/014311698215973) (Less=Better): {:.2f}".format(scc(opencv_image, con_img)))
    except:
        pass



