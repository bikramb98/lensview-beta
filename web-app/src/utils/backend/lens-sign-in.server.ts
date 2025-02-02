import {ethers} from "ethers";
import {createClient} from "@urql/core";

import challenge from "../../graphql/challenge";
import authenticate from "../../graphql/authenticate";
import getDefaultProfile from "../../graphql/getDefaultProfile";

import {API_KEY, APP_ADDRESS, PRIVATE_KEY} from "$env/static/private";
import {PUBLIC_LENS_API_URL} from "$env/static/public";
import {logger} from "../../log/logManager";


let accessTokenFromLens;
let isSignedIn = false;
let signer;
let profile;


let client = createClient({
    url: PUBLIC_LENS_API_URL
});


/**
 * 2. i. Sign In with Lens
 *    ii. Get Access Token
 *    iii. Update Client with new Access Token
 */
export const signInWithLens = async () => {
    logger.info("utils/backend: lens-sign-in :: " + "EXECUTION START: signInWithLens");
    try {
        // console.log(challenge);
        /* first request the challenge from the API server */
        const challengeInfo = await client.query(challenge, {address: APP_ADDRESS}).toPromise();
        const provider = new ethers.providers.AlchemyProvider("maticmum", API_KEY);

        signer = new ethers.Wallet(PRIVATE_KEY, provider);
        /* ask the user to sign a message with the challenge info returned from the server */
        const signature = await signer.signMessage(challengeInfo.data.challenge.text);

        /* authenticate the user */
        const authData = await client.mutation(authenticate, {address: APP_ADDRESS, signature: signature}).toPromise();
        /* if user authentication is successful, you will receive an accessToken and refreshToken */
        const {
            data: {
                authenticate: {accessToken}
            }
        } = authData
        accessTokenFromLens = accessToken;

        /** you can now use the accessToken to make authenticated requests to the API server **/
        /** Update client with new accessToken **/
        client = createClient({
            url: PUBLIC_LENS_API_URL,
            fetchOptions: {
                headers: {
                    'x-access-token': `Bearer ${accessTokenFromLens}`
                },
            },
        });
        isSignedIn = true;

        /** Getting profile of the connected user and saving it to "profile" variable **/
        profile = await getUserProfile();
        if (profile != null) {
            logger.info("utils/backend: lens-sign-in :: " + "EXECUTION END: signInWithLens: " + "SUCCESSFUL");
            return [client, signer, profile];
        } else {
            return null
        }

    } catch (error) {
        logger.error("utils/backend: lens-sign-in :: " + "EXECUTION END: signInWithLens: " + "FAILED: " + error);
        return null;
    }
}

const getUserProfile = async () => {
    logger.info("utils/backend: lens-sign-in :: " + "EXECUTION START: getUserProfile");
    try {
        const response = await client.query(getDefaultProfile, {
            address: APP_ADDRESS
        }).toPromise();
        const defaultProfile = response.data.defaultProfile;
        logger.info("utils/backend: lens-sign-in :: " + "EXECUTION END: getUserProfile: " + "SUCCESSFUL: Signed in with: " + defaultProfile);
        return defaultProfile;
    } catch (error) {
        logger.error("utils/backend: lens-sign-in :: " + "EXECUTION END: getUserProfile: " + "FAILED: Failed to Sign In " + error);
        return null
    }
};

