
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

'''
{'date': 'Wed, 10 Nov 2021 12:12:08 GMT', 'server': 'Apache/2.4.25 (FreeBSD) OpenSSL/1.0.2u-freebsd PHP/7.4.15', 
'last-modified': 'Mon, 25 Oct 2021 17:48:47 GMT', 'etag': '"b-5cf30f914cb18"', 'accept-ranges': 'bytes', 
'content-length': '11', 'content-type': 'text/plain', 'http': 'HTTP/1.1 200 OK', 'body': 'Cras nunc.\n'}

{'date': 'Wed, 10 Nov 2021 12:12:29 GMT', 'server': 'Apache/2.4.25 (FreeBSD) OpenSSL/1.0.2u-freebsd PHP/7.4.15', 
'content-length': '238', 'content-type': 'text/html; charset=iso-8859-1', 
'http': 'HTTP/1.1 404 Not Found', 
'body': '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n<html><head>\n<title>404 Not Found</title>\n</head><body>\n<h1>Not Found</h1>\n<p>The requested URL /~cs421/fall21/project1/files2/dummy5.txt was not found on this server.</p>\n</body></html>\n'}
'''

import socket
import argparse
import os
import sys
class FileDownloader:

    @classmethod
    def separate_website_and_file_names(cls,url):
        ''' 
        takes the url and seperates the filename and host addr
        return [host_addr, file_name]
        '''
        website_url = url.split('/')[0]
        file_name = ''.join(url.partition('/')[1:])
        return[website_url, file_name]

    @classmethod
    def formatted_http_get(cls,file_name,host_addr):
        return "GET /{0} HTTP/1.1\r\nHost:{1}\r\n\r\n".format(file_name,host_addr)

    @classmethod
    def formatted_http_partial_get(cls,file_name ,host_addr ,range):
        return   "GET {0} HTTP/1.1\r\nhost:{1}\r\nrange: bytes={2}\r\n\r\n".format(file_name,host_addr,range) 

    @classmethod
    def formatted_http_head(cls,file_name,host_addr):
        return "HEAD /{0} HTTP/1.1\r\nHost:{1}\r\n\r\n".format(file_name,host_addr)

    @classmethod
    def create_socket(cls):
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()
        return my_socket

    @classmethod
    def connect_to_host(cls,host_addr,my_socket, port):
        try:
            index_file_ip = socket.gethostbyname( host_addr )
        except socket.gaierror:
            print('index_file_host ip could not be recieved, exiting')
            sys.exit()

        my_socket.connect(( index_file_ip, port))

    @classmethod    
    def close_socket(cls,my_socket):
        my_socket.close

    @classmethod
    def get_index_file_list(cls,string):
        index_file_addresses = string.split('\n')
        index_file_addresses.pop()
        return index_file_addresses

    @classmethod
    def dictify_response(cls,response):
       
        header, _, body = response.partition('\r\n\r\n')
        header = header.split('\r\n')
        header.append(body)
        json_data = {}
        new_header = header [1:len(header)-1]
        for b in new_header:
            i = b.split(': ')
            json_data[i[0].lower()] = i[1]
        json_data['http'] = header[0]
        json_data['body'] = header[len(header)-1]
        return json_data

    @classmethod
    def send_http_req(cls,host_addr,http_req, port):
        '''sends http request and returns the response as a dictionary '''
        my_socket = cls.create_socket() 
        cls.connect_to_host(host_addr, my_socket,port)
        response = ''
        my_socket.sendall(http_req.encode('utf-8'))
        while True:
            recv = my_socket.recv(2048)
            if recv == b'':
                break
            response += recv.decode()
        cls.close_socket(my_socket)
        dict_res = cls.dictify_response(response)
        return dict_res

    @classmethod
    def download_index_files_ranged(cls,file_list, port, lower_endpoint, upper_endpoint):
        '''
        downloads the elements from the list, first sends a HEAD and then sends a get
        '''
        range = '{}-{}'.format(lower_endpoint,upper_endpoint)
        
        for index, value in enumerate(file_list, 1):
            temp = cls.separate_website_and_file_names(value)
            host_addr = temp[0]
            file_name = temp[1]
            req = cls.formatted_http_head(file_name,host_addr)
            dict_res = cls.send_http_req(host_addr, req,port)
            if dict_res['http'] != 'HTTP/1.1 200 OK':
                print('{}. {} {}'.format(index, value, 'is not found'))
                continue
            if 'content-length' in dict_res:
                if int (dict_res['content-length']) < int(lower_endpoint):
                    print('{}. {} (size = {}) (range = {}) {}'.format(index, value,dict_res['content-length'], range ,'is not downloaded'))
                    continue
            if 'content-length' not in dict_res:
                if int(lower_endpoint) > 0:
                    print('{}. {} (size = {}) (range = {}) {}'.format(index, value,0, range ,'is not downloaded'))
                    continue
            req = cls.formatted_http_partial_get(file_name,host_addr,range)
            dict_res = cls.send_http_req(host_addr, req,port)
            a =  file_name.split('/')
            b = a[len(a)-1]
            with open("{}".format(os.getcwd() + '/{}'.format(b)), "w") as text_file:
                text_file.write(dict_res['body'])
            if 'content-length' not in dict_res:
                print('{}. {} (size = {}) (range = {}) {}'.format(index, value,0, range ,'is downloaded'))
                continue
            if int(dict_res['content-length']) >= int(upper_endpoint):
                print('{}. {} (size = {}) (range = {} ) {}'.format(index, value, dict_res['content-length'] ,range ,'is downloaded'))
                continue
            if  int(dict_res['content-length']) < int(upper_endpoint):
                print('{}. {} (size = {}) (range = {} ) {}'.format(index, value, dict_res['content-length'] ,
                    '{}-{}'.format(lower_endpoint, int(dict_res['content-length']) + int(lower_endpoint) - 1 ) ,'is downloaded'))
                continue

    @classmethod
    def download_index_files(cls,file_list, port):
        '''
        downloads the elements from the list, first sends a HEAD and then sends a get
        '''
        for index, value in enumerate(file_list, 1):
            temp = cls.separate_website_and_file_names(value)
            host_addr = temp[0]
            file_name = temp[1]
            req = cls.formatted_http_head(file_name,host_addr)
            dict_res = cls.send_http_req(host_addr, req,port)
            a =  file_name.split('/')
            b = a[len(a)-1]
            if dict_res['http'] != 'HTTP/1.1 200 OK':
                print('{}. {} {}'.format(index, value, 'is not found'))
                continue
            req = cls.formatted_http_get(file_name,host_addr)
            dict_res = cls.send_http_req(host_addr, req,port)
            a =  file_name.split('/')
            b = a[len(a)-1]
            with open("{}".format(os.getcwd() + '/{}'.format(b)), "w") as text_file:
                text_file.write(dict_res['body'])
            if 'content-length' not in dict_res:
                print('{}. {} (size = {}) {}'.format(index, value,0, 'is downloaded'))
                continue
            print('{}. {} (size = {}) {}'.format(index, value, dict_res['content-length'],'is downloaded'))
    

################################################################################

if __name__ == '__main__':
    PORT = 80
    lower_endpoint = ''
    upper_endpoint = ''
    use_range = False

    parser = argparse.ArgumentParser(description='downloads files within requested size parametes')

    parser.add_argument('index_file',  nargs=1 ,metavar='index_file', type=str, help='enter the address of the index file')
    parser.add_argument('range', metavar='range', type=str, nargs='?' ,help='enter lower and upper endpoints with \'-\' in between')
    args = parser.parse_args()
    index_file = args.index_file[0]
    range = args.range
  
    if args.range:
        if '-' in range:
            if len(range.split('-')) == 2:
                str = range.split('-')
                lower_endpoint = str[0]
                upper_endpoint = str[1]
                use_range = True
            else:
                print('final argument should be in the form <lower endpoint>-<upper endpoint>')
                sys.exit()
        else: 
            print('final argument should be in the form \'<lower endpoint>-<upper endpoint>')
            sys.exit()  

    print('URL of the index file:', index_file)
    if use_range:
        print('Lower endpoint:', lower_endpoint )
        print('Upper endpoint:', upper_endpoint )
    else:
        print('No range is given')

    host_and_fname = FileDownloader.separate_website_and_file_names(index_file)
    
    request = FileDownloader.formatted_http_get(host_and_fname[1], host_and_fname[0])
    josn_res = FileDownloader.send_http_req(host_and_fname[0], request,PORT)
    addr_list = FileDownloader.get_index_file_list(josn_res['body'])

    print('There are {} files in the index '.format(len(addr_list)))

    if use_range:
        FileDownloader.download_index_files_ranged(addr_list, PORT, lower_endpoint, upper_endpoint)
    else:
        FileDownloader.download_index_files(addr_list, PORT)








