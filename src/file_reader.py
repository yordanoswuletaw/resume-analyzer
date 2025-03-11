import cv2
from glob import glob
import numpy as np
from pdf2image import convert_from_path
from pypdf import PdfReader
import pytesseract
from tqdm import tqdm
import os
from collections import defaultdict

class FileReader:
    """
    A class to read and process job description (JD) files and resume files from specified directories.
    """
    def __init__(self, jd_path, resume_path):
        """
       Initializes the DirectoryReader with paths to job descriptions and resumes.

       Args:
           jd_path (str): Path to the directory containing job description files.
           resume_path (str): Path to the directory containing resume files.
       """
        self.jds_path = jd_path
        self.resumes_path = resume_path

        self.jd_data = defaultdict(str)
        self.resume_data = defaultdict(str)

    def read_jd_data(self):
        """
        Reads job description files from the specified directory and stores the content in jd_data attribute.

        Returns:
            dict: A dictionary with job names as keys and the corresponding job descriptions as values.
        """
        files = glob(self.jds_path, recursive=True)
        for file in files:
            with open(file, 'rb') as f:
                data = f.read().strip().lower()
                data = b'{data}'.decode("utf-8")
                job_label = file.split('/')[-1].replace('.txt', '')
                self.jd_data[job_label] = data
        return self.jd_data

    @staticmethod
    def extract_text_from_pdf(file):
        reader = PdfReader(file)
        data = ""
        for page in reader.pages:
            data = data + page.extract_text() + "\n"
        data = data.strip().lower()
        return data

    def extract_text_from_image(self, file):
        pages = convert_from_path(file)
        extracted_text = []
        for page in pages:
            # Step 1: Preprocess the image (deskew)
            preprocessed_image = self.deskew(np.array(page))
            # Step 2: Extract text using OCR
            text = self.get_text_from_image(preprocessed_image)
            extracted_text.append(text)
        return "\n".join(extracted_text).strip().lower()

    def read_resume_data(self):
        """
        Reads resume files from the specified directory and stores the content in resume_data attribute.
        If the resume file is a PDF containing images, OCR is used to extract text.

        Returns:
            dict: A dictionary with resume identifiers as keys and the corresponding resume texts as values.
        """
        file_list = glob(self.resumes_path, recursive=True)
        for file in tqdm(file_list):
            file_parts = os.path.normpath(file).split(os.sep)
            # The job title would be the name of the directory just before the file name
            job_title = file_parts[-2].replace(" ", "_").lower()      
            # The resume name would be the file name without the extension
            resume_name = os.path.basename(file_parts[-1]).replace("-", "_").lower().replace(".pdf", "")   
            data = self.extract_text_from_pdf(file)
            if len(data) > 1:
                self.resume_data[job_title + "_" + resume_name] = data
            else:  # to solve for incorrect startxref pointer(3), since they are images in pdf
                self.resume_data[job_title + "_" + resume_name] = self.extract_text_from_image(file)
        return self.resume_data


    @staticmethod
    def deskew(image):
        """
       Deskews the given image to correct any tilt.

       Args:
           image (numpy.ndarray): The image to be deskewed.

       Returns:
           numpy.ndarray: The deskewed image.
       """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    @staticmethod
    def get_text_from_image(image):
        """
       Extracts text from the given image using OCR.

       Args:
           image (numpy.ndarray): The image from which to extract text.

       Returns:
           str: The extracted text.
       """
        text = pytesseract.image_to_string(image)
        return text
