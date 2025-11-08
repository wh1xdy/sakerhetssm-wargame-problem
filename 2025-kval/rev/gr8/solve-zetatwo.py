#!/usr/bin/env python3

import ast
import re

import numpy as np
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("http://localhost:50000/")
matrices = []
images = driver.find_elements(By.TAG_NAME, "img")
for image in images:
    if (src := image.get_attribute('src')) == None:
        continue
    if not re.search(r'/m\d+\.png', src):
        continue
    transform = image.value_of_css_property('transform')
    
    matrix = ast.literal_eval(transform.removeprefix('matrix'))[:-2]
    matrices.append(matrix)

flag = []
for matrix in matrices:
    matrix = np.matrix(matrix).reshape((2,2)).transpose()
    inverse = np.linalg.inv(matrix)
    part = [round(x) for x in inverse.reshape(1, 4).tolist()[0]]
    flag += part

print(bytes(flag).decode())
