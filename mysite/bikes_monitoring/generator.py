import random
from string import ascii_letters, digits


class Generator:

    # Generate token wit float lenght
    def token_gen(self, length=None):
        if length == None:
            length = 64
        token_secure = None
        
        symbols =ascii_letters + digits
        rand = random.SystemRandom()
        token = "".join(rand.choice(symbols) for i in range(length))
        
        return(self.make_token_file(token=token))
    

    #write token to file
    def make_token_file(self, token, file_name=None):
        if file_name == None:
            file_name = "token.txt"

        try:
            with open("token/" + file_name, "w") as f:
                print(token, file=f)
                
            return "Done"
        except:
            return "Unable to write token!"