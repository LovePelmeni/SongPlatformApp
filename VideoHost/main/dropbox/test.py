import dropbox

DROPBOX_ACCESS_KEY = 'bep2nuhf1wmtq3y'
DROPBOX_ACCESS_SECRET = 't2nfz143f8iqdc9'

dropbox_app = dropbox.dropbox_client.Dropbox(
oauth2_access_token='sl.BJLitAO_iWxsZEgUxIeUrWshvSSn5sX2Zur9qk7u9N_k0d-9kJ5tLrAIEKWNNsjay3u4z4sIgvspeuIa_eNFP4SQ1sXF7Jpxad3ibll70lpU9Qbon_HG11Vk8rgSpRAS1rh-OSI',
)

with open('../tests/avatar.jpeg', mode='rb') as file:
    dropbox_app.files_upload(path='/some/path/avatar.jpeg', f=file.read())




