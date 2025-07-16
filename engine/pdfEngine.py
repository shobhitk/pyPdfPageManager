import os
import json
import pypdf
from pprint import pprint

class PdfEngine():
    """PDF Class object to manage and generate PDF Setup files and PDF files.
    """
    def __init__(self):
        pass

    def get_doc_basename(self, document):
        """Returns basename of document.

        Args:
            document (string): File Path.

        Returns:
            string: Path basename.
        """
        return os.path.basename(document).split(".")[0]

    
    def get_pdf_pages(self, document):
        """Returns Pages of the document.

        Args:
            document (string): Path of PDF file.

        Returns:
            list: Returns list of PageObjects.
        """
        pdf_read_obj = pypdf.PdfReader(document)
        if pdf_read_obj.is_encrypted:
            pdf_read_obj.decrypt("AES-256")
        pages = pdf_read_obj.pages
        return pages


    def get_pdf_url(self, pdf_file):
        """Generate and Return pdf URL 

        Args:
            pdf_file (string): PDF path.
                # Example URL"file:////www.example.com/myfile.pdf">

        Returns:
            string: PDF URL.
        """
        return "file:////{0}".format(pdf_file)

    
    def load_setup(self, load_file):
        """Reads PDF setup file and returns PDF Setup Dict

        Args:
            load_file (string): Setup File JSON.

        Returns:
            dict: Setup dictionary.
        """
        with open(load_file, "r") as f:
            pdf_dict = json.load(f)

        return pdf_dict


    def save_setup(self, data, save_file):
        """Saves the PDF Setup data and saves the JSON file.

        Args:
            data (dict): PDF Setup Data dict.
            save_file (string): Setup JSON filepath.
        """
        if not os.path.isdir(os.path.dirname(save_file)):
            os.makedirs(os.path.dirname(save_file))
        with open(save_file, "w+") as f:
            json.dump(data, f, indent=4)


    def generate_dict(self, document_list, output_folder):
        """Generate current PDF Setup dictionary from the document list.

        Args:
            document_list (list): List of PDF files.
            output_folder (string): Path of output file.

        Returns:
            dict: Split PDF Setup dictionary.
        """
        def_dict = {
            "output_dir": output_folder,
        }

        for document in document_list:
            doc_name = self.get_doc_basename(document)
            def_dict[doc_name] = {}
            pages = self.get_pdf_pages(document)
            for page_num in range(len(pages)):
                def_dict[doc_name][str(page_num + 1)] = {str(page_num + 1): document}
        return def_dict
    

    def generate_merged_dict(self, document_list, output_folder):
        """Generate Merged PDF Setup dictionary from the document list.

        Args:
            document_list (list): List of PDF files.
            output_folder (string): Path of output file.

        Returns:
            dict: Merged PDF Setup dictionary.
        """
        merged_doc_name = self.get_doc_basename(document_list[0]) + "_MERGED"
        merge_dict = {
            "output_dir": output_folder,
            merged_doc_name: {}
        }
        output_page_number = 1
        for document in document_list:
            pages = self.get_pdf_pages(document)
            for page_num in range(len(pages)):
                merge_dict[merged_doc_name][str(output_page_number)] = {str(page_num + 1): document}
                output_page_number += 1

        return merge_dict
    

    def generate_split_dict(self, document_list, output_folder):
        """Generate Split PDF Setup dictionary from the document list.

        Args:
            document_list (list): List of PDF files.
            output_folder (string): Path of output file.

        Returns:
            dict: Split PDF Setup dictionary.
        """
        split_dict = {
            "output_dir": output_folder,
        }
        for document in document_list:
            pages = self.get_pdf_pages(document)
            for page_num in range(len(pages)):
                split_doc_name = self.get_doc_basename(document) + "_" + str(page_num + 1)
                split_dict[split_doc_name] = {"1": {str(page_num + 1): document}}

        return split_dict


    def extract_input_files(self, pdf_dict):
        """Extract Input files from PDF Setup dict.

        Args:
            pdf_dict (dict): PDF Setup dict.

        Returns:
            list: list of source files.
        """
        files = []
        for doc_key, doc_val in pdf_dict.items():
            if doc_key == "output_dir":
                continue
            
            for page_key in doc_val.keys():
                page_val = doc_val[page_key]
                input_page = next(iter(page_val))
                input_doc = page_val[input_page]
                if input_doc not in files:
                    files.append(input_doc)

        return files

    
    def generate_pdfs(self, pdf_dict):
        """Method to generate PDF files based on PDF Setup dict.

        Args:
            pdf_dict (dict): PDF Setup dict.

        Returns:
            list: list of output paths.
        """
        output_dir = pdf_dict["output_dir"]
        out_paths = []
        for doc_key, doc_val in pdf_dict.items():
            pdf_write_obj = pypdf.PdfWriter()
            if doc_key == "output_dir":
                continue
            
            for page_key, page_val in doc_val.items():
                input_page = next(iter(page_val))
                input_doc = open(page_val[input_page], "rb")
                pdf_write_obj.append(
                    fileobj=input_doc, pages=(int(input_page)-1, int(input_page)))
            
            out_path = os.path.join(output_dir, doc_key + ".pdf")
            output = open(out_path, "wb")
            pdf_write_obj.write(output)
            pdf_write_obj.close()
            output.close()
            out_paths.append(out_path)
        
        return out_paths


