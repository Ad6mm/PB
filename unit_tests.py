import photon_beetle as pb
import subprocess
import random
import time

# K - klucz - KN_BITS[:128]
# N - nonce - KN_BITS[128:]
# AD - associated data - AD_BITS

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

unit_tests_iterations = 10

client_IP = "127.0.0.1"
server_IP = "127.0.0.1"
n_bytes = 256//8
rand_hex_from_openssl = subprocess.run(['openssl', 'rand','-hex',f'{n_bytes}'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]

def int_to_bin(a, total_length):
    return list(map(int,format(a, f'0{total_length}b')))

KN_BITS = []
for i in rand_hex_from_openssl:
    KN_BITS += int_to_bin(int(i,16),4)

AD_BITS = []
for i in (client_IP+"."+server_IP).split("."):
    AD_BITS += int_to_bin(int(i),8)
AD_data_str = "".join(map(str, AD_BITS))
KN_data_str = "".join(map(str, KN_BITS))

print("Associated data:", AD_data_str)
print("KN:", KN_data_str)
print()


def send_enc_print(msg_to_encrypt):
    msg_encrypted, tag = enc_str(msg_to_encrypt)
    print("Encrypted message:", msg_encrypted.encode('utf-8').hex())
    return msg_encrypted + "<-,->" + tag

def enc_str(msg_to_encrypt:str):
    M_bits_lst = pb.str_to_bits_list(msg_to_encrypt)
    C_bits_lst , T_bits_lst = pb.photon_beetle_enc(KN_BITS[:128], KN_BITS[128:], AD_BITS, M_bits_lst)
    C_assci_str = pb.bits_list_to_str(C_bits_lst)
    T_assci_str = pb.bits_list_to_str(T_bits_lst)
    return [C_assci_str,T_assci_str]

def recv_dec_print(encrypted):
    msg_encrypted, tag = encrypted.split("<-,->")
    decrypted = dec_str(msg_encrypted, tag)
    print("Decrypted message:", decrypted)
    return decrypted

def dec_str(cipher_text:str, tag_str:str):
    C_BITS = pb.str_to_bits_list(cipher_text)
    T_BITS = pb.str_to_bits_list(tag_str)
    M_bits_list , my_T_bits_list = pb.photon_beetle_dec(KN_BITS[:128], KN_BITS[128:], AD_BITS, C_BITS, T_BITS)
    M_assci_str = pb.bits_list_to_str(M_bits_list)
    my_T_str = pb.bits_list_to_str(my_T_bits_list)
    if my_T_str == tag_str:
        return M_assci_str
    else:
        return "Tag not verified"

unit_tests = input("Start unit tests? [True/False] ") == "True"

while not unit_tests:
    msg_to_encrypt = input("Message to encypt -> ")
    if msg_to_encrypt == "exit":
        break
    encrypted = send_enc_print(msg_to_encrypt)
    recv_dec_print(encrypted)
    
if unit_tests:
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(unit_tests_iterations):
        print(bcolors.HEADER + "Test", i+1, "of", unit_tests_iterations, "...", bcolors.ENDC)
        random_message = ''.join(random.choice(characters) for i in range(random.randint(1, 100)))
        print("Random message:", random_message)
        print("Message length:",len(random_message))
        start_time = time.time()
        encrypted = send_enc_print(random_message)
        enc_time = time.time() - start_time
        print("Encryption time:", enc_time)
        start_time = time.time()
        decrypted = recv_dec_print(encrypted)
        dec_time = time.time() - start_time
        print("Dencryption time:", dec_time)
        
        f = open("time_results.txt", "a")
        f.write("%s %s %s\n"%(len(random_message), enc_time, dec_time))
        f.close()
        
        assert random_message == decrypted
        print(bcolors.OKGREEN + "Assertion passed!", bcolors.ENDC)
        print()
        
print("Program stopped...")

