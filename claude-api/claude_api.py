import json
import os
import uuid
from curl_cffi import requests
import requests as req
import re


class Client:

  def __init__(self, cookie):
    self.cookie = cookie
    self.organization_id = self.get_organization_id()

  def get_organization_id(self):
    url = "https://claude.ai/api/organizations"

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}'
    }

    response = requests.get(url, headers=headers,impersonate="chrome110")
    res = json.loads(response.text)
    uuid = res[0]['uuid']

    return uuid

  def get_content_type(self, file_path):
    # Function to determine content type based on file extension
    extension = os.path.splitext(file_path)[-1].lower()
    if extension == '.pdf':
      return 'application/pdf'
    elif extension == '.txt':
      return 'text/plain'
    elif extension == '.csv':
      return 'text/csv'
    # Add more content types as needed for other file types
    else:
      return 'application/octet-stream'

  # Lists all the conversations you had with Claude
  def list_all_conversations(self):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations"

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}'
    }

    response = requests.get(url, headers=headers,impersonate="chrome110")
    conversations = response.json()

    # Returns all conversation information in a list
    if response.status_code == 200:
      return conversations
    else:
      print(f"Error: {response.status_code} - {response.text}")

  # Send Message to Claude
  def send_message(self, prompt, conversation_id, attachments=None,timeout=500):
    url = "https://claude.ai/api/append_message"

    # Initialize an empty attachments list
    uploaded_attachments = []

    # Upload each attachment if provided
    if attachments:
        for attachment in attachments:
            attachment_response = self.upload_attachment(attachment)
            if attachment_response:
                uploaded_attachments.append(attachment_response)
            else:
                return {"Error: Invalid file format for {}. Please try again.".format(attachment)}

    payload = json.dumps({
        "completion": {
            "prompt": f"{prompt}",
            "timezone": "Asia/Kolkata",
            "model": "claude-2"
        },
        "organization_uuid": f"{self.organization_id}",
        "conversation_uuid": f"{conversation_id}",
        "text": f"{prompt}",
        "attachments": uploaded_attachments
    })

    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept': 'text/event-stream, text/event-stream',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Origin': 'https://claude.ai',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'TE': 'trailers'
    }

    response = requests.post( url, headers=headers, data=payload,impersonate="chrome110",timeout=500)
    decoded_data = response.content.decode("utf-8")
    decoded_data = re.sub('\n+', '\n', decoded_data).strip()
    data_strings = decoded_data.split('\n')
    completions = []
    for data_string in data_strings:
      json_str = data_string[6:].strip()
      data = json.loads(json_str)
      if 'completion' in data:
        completions.append(data['completion'])

    answer = ''.join(completions)

    # Returns answer
    return answer

  # Deletes the conversation
  def delete_conversation(self, conversation_id):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}"

    payload = json.dumps(f"{conversation_id}")
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'Content-Length': '38',
        'Referer': 'https://claude.ai/chats',
        'Origin': 'https://claude.ai',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        'TE': 'trailers'
    }

    response = requests.delete( url, headers=headers, data=payload,impersonate="chrome110")

    # Returns True if deleted or False if any error in deleting
    if response.status_code == 204:
      return True
    else:
      return False

  # Returns all the messages in conversation
  def chat_conversation_history(self, conversation_id):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}"

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}'
    }

    response = requests.get( url, headers=headers,impersonate="chrome110")
    

    # List all the conversations in JSON
    return response.json()

  def generate_uuid(self):
    random_uuid = uuid.uuid4()
    random_uuid_str = str(random_uuid)
    formatted_uuid = f"{random_uuid_str[0:8]}-{random_uuid_str[9:13]}-{random_uuid_str[14:18]}-{random_uuid_str[19:23]}-{random_uuid_str[24:]}"
    return formatted_uuid

  def create_new_chat(self):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations"
    uuid = self.generate_uuid()

    payload = json.dumps({"uuid": uuid, "name": ""})
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Origin': 'https://claude.ai',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Cookie': self.cookie,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers'
    }

    response = requests.post( url, headers=headers, data=payload,impersonate="chrome110")

    # Returns JSON of the newly created conversation information
    return response.json()

  # Resets all the conversations
  def reset_all(self):
    conversations = self.list_all_conversations()

    for conversation in conversations:
      conversation_id = conversation['uuid']
      delete_id = self.delete_conversation(conversation_id)

    return True

  def upload_attachment(self, file_path):
    if file_path.endswith('.txt'):
      file_name = os.path.basename(file_path)
      file_size = os.path.getsize(file_path)
      file_type = "text/plain"
      with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

      return {
          "file_name": file_name,
          "file_type": file_type,
          "file_size": file_size,
          "extracted_content": file_content
      }
    url = 'https://claude.ai/api/convert_document'
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Origin': 'https://claude.ai',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        'TE': 'trailers'
    }

    file_name = os.path.basename(file_path)
    content_type = self.get_content_type(file_path)

    files = {
        'file': (file_name, open(file_path, 'rb'), content_type),
        'orgUuid': (None, self.organization_id)
    }

    response = req.post(url, headers=headers, files=files)
    if response.status_code == 200:
      return response.json()
    else:
      return False
      

    
  # Renames the chat conversation title
  def rename_chat(self, title, conversation_id):
    url = "https://claude.ai/api/rename_chat"

    payload = json.dumps({
        "organization_uuid": f"{self.organization_id}",
        "conversation_uuid": f"{conversation_id}",
        "title": f"{title}"
    })
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'Referer': 'https://claude.ai/chats',
        'Origin': 'https://claude.ai',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        'TE': 'trailers'
    }

    response = requests.post(url, headers=headers, data=payload,impersonate="chrome110")

    if response.status_code == 200:
      return True
    else:
      return False
      
