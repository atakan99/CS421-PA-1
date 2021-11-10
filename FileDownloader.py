
'''
• Please refer to W3Cs RFC 2616 for details of the HTTP messages in general and RFC 7233 for details of range requests.     
• You will assume that <lower endpoint> and <upper endpoint> are both non-negative integers and <lower endpoint> 
    is not greater than <upper endpoint>. Note that there should be a hyphen ‘-’ character between the endpoints.

• You will assume that each line of the index file includes one file URL.
• You will assume that the name of each file in the index is unique.
• Your program will not save the index file to the local folder.
• Your program should print a message to the command-line to inform the user about the status of the files.
• The downloaded file should be saved under the directory containing the source file FileDownloader and the name 
    of the file should be the same as the name of the downloaded file.

• You may use the following URLs to test your program:
    www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt
    www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt
• Please contact your assistant if you have any doubt about the assignment.
'''

'''
HTTP/1.1 404 Not Found
HTTP/1.1 200 OK
'''

import socket
import argparse
import os
import sys
import ast
import json
import re

def separate_website_and_file_names(url):
    ''' 
    takes the url and seperates the filename and host addr
    return [host_addr, file_name]
    '''
    website_url = url.split('/')[0]
    file_name = ''.join(url.partition('/')[1:])
    return[website_url, file_name]

def formatted_http_get(file_name,host_addr):
    return "GET /{0} HTTP/1.1\r\nHost:{1}\r\n\r\n".format(file_name,host_addr)

def formatted_http_partial_get(file_name ,host_addr ,range):
    return   "GET {0} HTTP/1.1\r\nhost:{1}\r\nrange: bytes={2}\r\n\r\n".format(file_name,host_addr,range) 

def create_socket():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()
    return my_socket

def connect_to_host(host_addr,my_socket, port):
    try:
        index_file_ip = socket.gethostbyname( host_addr )
    except socket.gaierror:
        print('index_file_host ip could not be recieved, exiting')
        sys.exit()

    my_socket.connect(( index_file_ip, port))

def close_socket(my_socket):
    my_socket.close

def get_index_file_list(string):
    index_file_addresses = string.split('\n')
    index_file_addresses.pop()
    return index_file_addresses

def send_http_req(my_socket,http_req):
    '''sends http request and returns the response as a string'''
    response = ''
    my_socket.sendall(http_req.encode('utf-8'))
    while True:
        recv = my_socket.recv(1024)
        if recv == b'':
            break
        response += recv.decode()
    return response

def jsonify(response):
    header, _, body = response.partition('\r\n\r\n')
    #print(header)
    #print(body)
    header = header.split('\r\n')
    body = body
    header.append(body)
    #print(header)
    d = {}
    new_header = header [1:len(header)-1]
    #print(new_header)
    for b in new_header:
        i = b.split(': ')
        d[i[0].lower()] = i[1]
    d['http'] = header[0]
    d['body'] = header[len(header)-1]
    return d

def download_index_files_ranged(file_list, range = '0-0'):
   return
    

def download_index_files(file_list, my_socket, port):
    print(file_list)
    for i in file_list:
        temp = separate_website_and_file_names(i)
        host_addr = temp[0]
        file_name = temp[1]
        my_socket = create_socket() 
        connect_to_host(host_addr, my_socket,PORT)
        req = formatted_http_get(file_name,host_addr)
        answer_str = send_http_req(my_socket, req)
        close_socket(my_socket)
        json_res = jsonify(answer_str)
        a =  file_name.split('/')
        b = a[len(a)-1]
        if json_res['http'] == 'HTTP/1.1 200 OK':
            with open("{}".format(os.getcwd() + '/{}'.format(b)), "w") as text_file:
                text_file.write(json_res['body'])


parser = argparse.ArgumentParser(description='downloads files within requested size parametes')

parser.add_argument('index_file',  nargs=1 ,metavar='index_file', type=str, help='enter the address of the index file')
parser.add_argument('range', metavar='range', type=str, nargs='?' ,help='enter lower and upper endpoints with \'-\' in between')
args = parser.parse_args()
index_file = args.index_file[0]
range = args.range
lower_endpoint = ''
upper_endpoint = ''
use_range = False


print('URL of the index file:', index_file)
if args.range:
    str = range.split('-')
    lower_endpoint = str[0]
    upper_endpoint = str[1]
    print('Lower endpoint:', lower_endpoint )
    print('Upper endpoint:', upper_endpoint )
    use_range = True
else:
    print('No range is given')    

PORT = 80

foo = separate_website_and_file_names(index_file)

my_socket = create_socket() 

connect_to_host(foo[0], my_socket,PORT)

response = ''
# request = "GET /{0} HTTP/1.1\r\nHost:{1}\r\n\r\n".format(index_file_file,index_file_host)
request = formatted_http_get(foo[1], foo[0])
response = send_http_req(my_socket,request)
#print(response)
http_json = jsonify(response)
#print(http_json)
addr_list = get_index_file_list(http_json['body'])
#print(addr_list)
#print(index_file_addresses)
print('There are {} files in the index '.format(len(addr_list)))

close_socket(my_socket)
download_index_files(addr_list, my_socket, PORT)


##print('response', list(response.partition('\r\n\r\n')).split('\n'))
'''
close_socket(my_socket)



b = separate_website_and_file_names('www.cs.bilkent.edu.tr/~cs421/fall21/project1/files2/dummy5.txt')

my_socket = create_socket()

connect_to_host(b[0], my_socket, PORT)

response = ''
if use_range:
    request2 = formatted_http_partial_get(b[1], b[0], range)
    response = send_http_req(my_socket, request2)
    #print(response)
    print(jsonify(response))


'''


 #request2 = "GET /{0} HTTP/1.1\r\nHost:{1}\r\n\r\n".format(b[1],b[0])
    #print(request2)
'''
data_ls = []
while True:
    data = my_socket.recv(2048)
    if not data: # after getting the first data
        break #    Python wont come to this "if" so it wont break!

    data = data.decode('utf-8')
    data_ls.append(data)
print('-----',data_ls)
'''











