import json
import os
import smtplib
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from email.message import EmailMessage


def send_email(subject, body, to_email):
    # Read the parameters from the JSON file
    credentials_json_file_path = 'credentials.json'
    
    if os.path.exists(credentials_json_file_path):
        with open(credentials_json_file_path, 'r') as f:
            params = json.load(f)
            from_email = params.get('email')
            from_password = params.get('password')
            
            if from_email and from_password:
                # Create the email
                msg = EmailMessage()
                msg.set_content(body)
                msg['Subject'] = subject
                msg['From'] = from_email
                msg['To'] = to_email

                # Send the email
                smtp = smtplib.SMTP('smtp.office365.com', 587)  # Use the appropriate SMTP server and port
                smtp.starttls()
                smtp.login(from_email, from_password)
                smtp.send_message(msg)
            else:
                print("Missing one or more parameters in the JSON file.")
    else:
        print(f"JSON file '{credentials_json_file_path}' not found.")

def check_availability(url, size, to_email, company):
    driver = webdriver.Firefox()
    
    driver.implicitly_wait(5)
    driver.get(url)
    time.sleep(5)

    is_sale = False
    is_in_stock = False

    if company == "pullandbear":

        #İndirim Kontrolü

        try:
            if driver.find_element(By.XPATH,'//*[@id="productCard"]/div/div/div[1]/div[1]/div[1][contains(@class, "sale")]/span'):
                is_sale = True
        except:
            pass
        
        #Beden - Numara Kontrolü

        try:
            ul_element = driver.execute_script('return document.querySelector("#productCard > div > div > div.c-product-info--size > size-selector-with-length").shadowRoot.querySelector("size-selector-select").shadowRoot.querySelector("div > div.size-list-select > size-list").shadowRoot.querySelector("ul")')

            li_elements = driver.execute_script('return arguments[0].querySelectorAll("li")',ul_element)

            for li in li_elements:
                button_and_class = driver.execute_script('''
                    var button = arguments[0].querySelector("button");
                    if (button) {
                        return { button: button, className: button.className };
                        }
                    return null;
                ''', li)
            
                if button_and_class:
                    button = button_and_class['button']
                    class_name = button_and_class['className']
                    
                    button_text = driver.execute_script('return arguments[0].querySelector("span.name").innerText', button)
                    
                    if button_text.strip() == size and "is-disabled" not in class_name:
                        is_in_stock = True
                        break
        except:
            pass

    elif company == "zara":

        #İndirim Kontrolü

        try:
            if driver.find_element(By.XPATH,'//*[@id="main"]/article/div[2]/div[1]/div[2]/div/div[1]/div[2]/div/span/span[2][contains(@class, "price__amount--on-sale")]'):
                is_sale = True
        except:
            pass
        
        #Beden - Numara Kontrolü

        try:
            element = driver.find_element(By.XPATH,'//*[@id="main"]/article/div[2]/div[1]/div[2]/div/div[2]/div/div[2]')

            ul_element = element.find_element(By.TAG_NAME, "ul")

            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

            for li in li_elements:
                
                item_size = li.find_element(By.CLASS_NAME, 'product-size-info__main-label').text.strip()
                li_classes = li.get_attribute('class')

                if item_size == size:
                    if 'size-selector-list__item--out-of-stock' not in li_classes:
                        is_in_stock = True
                        break
        except:
            pass

    print(is_sale)
    print(is_in_stock)

    if is_sale and is_in_stock:
        subject = f"{company} - Ürün hem indirimde hem de stokta!"
        body = f"Ürünün {size} bedeni-numarası hem indirimde hem stokta.\n Link'e tıklayarak ürüne gidebilirsin:\n {url}"
        send_email(subject, body, to_email)
        driver.quit()
        return True

    elif is_in_stock:
        subject = f"{company} - Ürün stokta!"
        body = f"Ürünün {size} bedeni-numarası stokta.\n Link'e tıklayarak ürüne gidebilirsin:\n {url}"
        send_email(subject, body, to_email)
        driver.quit()
        return True
    
    driver.quit()
    return False

def update_json_file(json_file_path, params):
    with open(json_file_path, 'w') as f:
        json.dump(params, f, indent=4)

def main():

    json_file_path = 'params.json'
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            params_list = json.load(f)
            
            for params in params_list:
                url = params.get('url')
                size = params.get('size')
                to_email = params.get('to_email')
                is_send = params.get('is_send')
                company = params.get("company")
                
                if url and size and to_email and is_send == "0":
                    if check_availability(url, size, to_email, company):
                        params['is_send'] = "1"
                    else:
                        params['is_send'] = "0"
                    update_json_file(json_file_path, params_list)
                else:
                    print("Skipping: Missing one or more parameters in the JSON file or is_send is not '0'.")
    else:
        print(f"JSON file '{json_file_path}' not found.")

if __name__ == "__main__":
    main()
