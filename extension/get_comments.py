import requests
import json

class GetComments:

    def __init__(self, hashedURL, lensID):

        self.lensid = lensID
        self.hashedURL = hashedURL
        self.url = "https://api-mumbai.lens.dev/"

    def get_post_id(self):

        payload = json.dumps({
        "query": "query Publications($hashedURL: String!, $lensId: ProfileId) {\n  publications(request: {\n    profileId: $lensId,\n    publicationTypes: [POST],\n    metadata: {\n      locale: \"en-us\"\n      tags: {\n        oneOf: [$hashedURL]\n      }\n    }\n  }) {\n    items { \n    ... on Post {\n      ...PostFields\n    }\n    ... on Comment {\n      ...CommentFields\n    }\n    ... on Mirror {\n      ...MirrorFields\n    }\n    }\n  }\n}\n\nfragment ProfileFields on Profile {\n  name\n  handle\n  picture {\n    ... on NftImage {\n      contractAddress\n      tokenId\n      uri\n      verified\n    }\n  }\n  ownedBy\n  dispatcher {\n    address\n  }\n}\n\nfragment PublicationStatsFields on PublicationStats { \n  totalAmountOfMirrors\n  totalAmountOfCollects\n  totalAmountOfComments\n  totalUpvotes\n}\n\nfragment MetadataOutputFields on MetadataOutput {\n  description\n  content\n  tags\n  image\n}\n\nfragment Erc20Fields on Erc20 {\n  name\n  symbol\n  decimals\n  address\n}\n\nfragment PostFields on Post {\n  id\n  profile {\n    ...ProfileFields\n  }\n  stats {\n    ...PublicationStatsFields\n  }\n  metadata {\n    ...MetadataOutputFields\n  }\n  createdAt\n  appId\n  hidden\n  reaction(request: null)\n  mirrors(by: null)\n}\n\nfragment MirrorBaseFields on Mirror {\n  id\n  profile {\n    ...ProfileFields\n  }\n  stats {\n    ...PublicationStatsFields\n  }\n  metadata {\n    ...MetadataOutputFields\n  }\n  createdAt\n  collectModule {\n    ...CollectModuleFields\n  }\n  referenceModule {\n    ...ReferenceModuleFields\n  }\n  appId\n  hidden\n  reaction(request: null)\n  hasCollectedByMe\n}\n\nfragment MirrorFields on Mirror {\n  ...MirrorBaseFields\n  mirrorOf {\n   ... on Post {\n      ...PostFields          \n   }\n   ... on Comment {\n      ...CommentFields          \n   }\n  }\n}\n\nfragment CommentBaseFields on Comment {\n  id\n  profile {\n    ...ProfileFields\n  }\n  stats {\n    ...PublicationStatsFields\n  }\n  metadata {\n    ...MetadataOutputFields\n  }\n  createdAt\n  appId\n  reaction(request: null)\n  mirrors(by: null)\n  hasCollectedByMe\n}\n\nfragment CommentFields on Comment {\n  ...CommentBaseFields\n  mainPost {\n    ... on Post {\n      ...PostFields\n    }\n    ... on Mirror {\n      ...MirrorBaseFields\n      mirrorOf {\n        ... on Post {\n           ...PostFields          \n        }\n        ... on Comment {\n           ...CommentMirrorOfFields        \n        }\n      }\n    }\n  }\n}\n\nfragment CommentMirrorOfFields on Comment {\n  ...CommentBaseFields\n  mainPost {\n    ... on Post {\n      ...PostFields\n    }\n    ... on Mirror {\n       ...MirrorBaseFields\n    }\n  }\n}\n\n\nfragment CollectModuleFields on CollectModule {\n  __typename\n  ... on FreeCollectModuleSettings {\n    type\n    followerOnly\n    contractAddress\n  }\n  ... on FeeCollectModuleSettings {\n    type\n    amount {\n      asset {\n        ...Erc20Fields\n      }\n      value\n    }\n    recipient\n    referralFee\n  }\n  ... on LimitedFeeCollectModuleSettings {\n    type\n    collectLimit\n    amount {\n      asset {\n        ...Erc20Fields\n      }\n      value\n    }\n    recipient\n    referralFee\n  }\n  ... on LimitedTimedFeeCollectModuleSettings {\n    type\n    collectLimit\n    amount {\n      asset {\n        ...Erc20Fields\n      }\n      value\n    }\n    recipient\n    referralFee\n    endTimestamp\n  }\n  ... on RevertCollectModuleSettings {\n    type\n  }\n  ... on TimedFeeCollectModuleSettings {\n    type\n    amount {\n      asset {\n        ...Erc20Fields\n      }\n      value\n    }\n    recipient\n    referralFee\n    endTimestamp\n  }\n  ... on UnknownCollectModuleSettings {\n    type\n    contractAddress\n    collectModuleReturnData\n  }\n}\n\nfragment ReferenceModuleFields on ReferenceModule {\n  ... on FollowOnlyReferenceModuleSettings {\n    type\n    contractAddress\n  }\n  ... on UnknownReferenceModuleSettings {\n    type\n    contractAddress\n    referenceModuleReturnData\n  }\n  ... on DegreesOfSeparationReferenceModuleSettings {\n    type\n    contractAddress\n    commentsRestricted\n    mirrorsRestricted\n    degreesOfSeparation\n  }\n}\n\n",
        "variables": {
            "hashedURL": self.hashedURL,
            "lensId": self.lensid
        }
        })
        headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://api-mumbai.lens.dev'
        }

        response = requests.request("POST", self.url, headers=headers, data=payload)

        response_data_json = json.loads(response.text)

        len_response_data = len(response_data_json['data']['publications']['items'])

        if len_response_data == 0:
            post_id = 0
        else:
            post_id = response_data_json['data']['publications']['items'][0]['id']

        return post_id

    def get_comments(self, post_id):

        comments_list = []
        user_handle = []

        payload = json.dumps({
        "query": "# Write your query or mutation here\nquery Publications($postid: InternalPublicationId) {\n  publications(request: {\n    commentsOf: $postid,\n    metadata: {\n      locale: \"en-us\"\n    }\n  }) {\n    items {\n    ... on Post {\n      ...PostFields\n    }\n    ... on Comment {\n      ...CommentFields\n    }\n    ... on Mirror {\n      ...MirrorFields\n    }\n    }\n  }\n}\n\nfragment MediaFields on Media {\n  url\n  mimeType\n}\n\nfragment ProfileFields on Profile {\n  id\n  name\n  attributes {\n    displayType\n    traitType\n    key\n    value\n  }\n  isFollowedByMe\n  isFollowing(who: null)\n  followNftAddress\n  metadata\n  isDefault\n  handle\n  picture {\n    ... on NftImage {\n      contractAddress\n      tokenId\n      uri\n      verified\n    }\n    ... on MediaSet {\n      original {\n        ...MediaFields\n      }\n    }\n  }\n  coverPicture {\n    ... on NftImage {\n      contractAddress\n      tokenId\n      uri\n      verified\n    }\n    ... on MediaSet {\n      original {\n        ...MediaFields\n      }\n    }\n  }\n  ownedBy\n}\n\nfragment PublicationStatsFields on PublicationStats { \n  totalAmountOfMirrors\n  totalAmountOfCollects\n  totalAmountOfComments\n  totalUpvotes\n}\n\nfragment MetadataOutputFields on MetadataOutput {\n  name\n  description\n  content\n  media {\n    original {\n      ...MediaFields\n    }\n  }\n  attributes {\n    displayType\n    traitType\n    value\n  }\n  tags\n}\n\n\nfragment PostFields on Post {\n  id\n  profile {\n    ...ProfileFields\n  }\n  stats {\n    ...PublicationStatsFields\n  }\n  metadata {\n    ...MetadataOutputFields\n  }\n  createdAt\n  appId\n  hidden\n  reaction(request: null)\n  mirrors(by: null)\n  hasCollectedByMe\n}\n\nfragment MirrorBaseFields on Mirror {\n  id\n  profile {\n    ...ProfileFields\n  }\n  stats {\n    ...PublicationStatsFields\n  }\n  metadata {\n    ...MetadataOutputFields\n  }\n  createdAt\n  appId\n  hidden\n  reaction(request: null)\n  hasCollectedByMe\n}\n\nfragment MirrorFields on Mirror {\n  ...MirrorBaseFields\n  mirrorOf {\n   ... on Post {\n      ...PostFields          \n   }\n   ... on Comment {\n      ...CommentFields          \n   }\n  }\n}\n\nfragment CommentBaseFields on Comment {\n  id\n  profile {\n    ...ProfileFields\n  }\n  stats {\n    ...PublicationStatsFields\n  }\n  metadata {\n    ...MetadataOutputFields\n  }\n  createdAt\n  appId\n}\n\nfragment CommentFields on Comment {\n  ...CommentBaseFields\n  mainPost {\n    ... on Post {\n      ...PostFields\n    }\n    ... on Mirror {\n      ...MirrorBaseFields\n      mirrorOf {\n        ... on Post {\n           ...PostFields          \n        }\n        ... on Comment {\n           ...CommentMirrorOfFields        \n        }\n      }\n    }\n  }\n}\n\nfragment CommentMirrorOfFields on Comment {\n  ...CommentBaseFields\n  mainPost {\n    ... on Post {\n      ...PostFields\n    }\n    ... on Mirror {\n       ...MirrorBaseFields\n    }\n  }\n}",
        "variables": {
            "postid": post_id
        }
        })
        headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://api-mumbai.lens.dev'
        }

        response = requests.request("POST", self.url, headers=headers, data=payload)
        response_data_json = json.loads(response.text)

        for i in range(len(response_data_json['data']['publications']['items'])):
            handle = response_data_json['data']['publications']['items'][i]['profile']['handle']
            comment = response_data_json['data']['publications']['items'][i]['metadata']['content']
            print("--xx--")
            print(comment)
            user_handle.append(handle)
            comments_list.append(comment)

        return comments_list, user_handle