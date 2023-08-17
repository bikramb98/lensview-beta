from urllib.parse import urlparse, urlunparse, ParseResult
import re

class URLProcessing():

    def get_cleaned_url(self, input_url):

        partly_cleaned_url = self.remove_ws_remove_www(input_url)

        cleaned_url, hostname, domain, path, query = self.preprocess_url(partly_cleaned_url)

        return cleaned_url, hostname, domain, path, query
    
    def strip_www(self, s):
        reg_exp = r'^(https?://)?(www\.)?(.*)'
        reg_exp_arr = re.match(reg_exp, s)
        if not reg_exp_arr:
            return s
        return f"{reg_exp_arr.group(1) if reg_exp_arr.group(1) else ''}{reg_exp_arr.group(3)}"

    def remove_ws_remove_www(self, url):
        # Remove whitespaces and the fragment(#) part of the URL
        url = url.strip().split('#')[0]
        # Remove www from the URL
        return self.strip_www(url)

    # url_input = "https://www.indiatoday.in/science/story/arab-astronaut-sultan-al-neyadi-shares-photo-delhi-space-independence-day-2421632-2023-08-15"
    # print("Input: ", url_input)
    # cleaned_url = remove_ws_remove_www(url_input)

    def preprocess_url(self, url):
        try:
            parsed_url = urlparse(url)

            if parsed_url.scheme in ['http', 'https']:
                # Remove extra '/' at the end of the pathname if it exists
                if parsed_url.path[-1] == '/' and len(parsed_url.path) > 1:
                    parsed_path = parsed_url.path[:-1]
                else:
                    parsed_path = parsed_url.path

                # Remove extra '/' from the url
                cleaned_path = '/'.join([segment for segment in parsed_path.split('/') if segment])
                parsed_result = ParseResult(parsed_url.scheme, parsed_url.netloc, cleaned_path, parsed_url.params, parsed_url.query, parsed_url.fragment)
                cleaned_url = urlunparse(parsed_result)

                hostname = parsed_url.hostname
                domain = hostname.split('.')[0]
                path = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_path}"
                query = parsed_url.query

                return cleaned_url.strip(), hostname.strip(), domain.strip(), path.strip(), query

            elif parsed_url.scheme == 'data':
                return parsed_url.geturl().strip(), None, None, None, None
            else:
                return None
        except:
            print('Failed to process URL')
            return None

# cleaned_url, hostname, domain, path, query = self.preprocess_url(cleaned_url)
# if cleaned_url is not None:
#     print("Cleaned URL:", cleaned_url)
#     print("Hostname:", hostname)
#     print("Domain:", domain)
#     print("Path:", path)
#     print("Query:", query)
# else:
#     print("Error processing URL.")

