<script lang="ts">
    import { cross, flightTakeoff, tick } from "../../utils/frontend/appIcon";
    import { isSignedIn } from "../../services/signInStatus";
    import { userProfile } from "../../services/profile";
    import checkTxHashBeenIndexed from "../../utils/checkTxHashBeenIndexed";
    import { page } from "$app/stores";
    import Loader from "$lib/Loader.svelte";
    import { reloadCommentOfAPublication } from "../../services/reloadPublication";
    import Login from "../Login.svelte";
    import postAPublication from "../../utils/frontend/postAPublication";
    import { goto } from "$app/navigation";
    import { getNotificationsContext } from "svelte-notifications";
    import GetTestMatic from "../GetTestMatic.svelte";
    import getPictureURL from "../../utils/frontend/getPictureURL";

    const {addNotification} = getNotificationsContext();
    let userEnteredContent = "";
    let inputInvalidReason = "";
    const wordLimit = 1000;
    let isInputInvalid = true;
    let showLoginModal = false;
    let postPubId = $page.data.postPubId;
    let isThisComment = postPubId !== undefined;
    let pubId = isThisComment ? postPubId : $page.data.mainPostPubId;
    let pubBtnName = isThisComment ? "Comment" : "Post";
    let showGetTestMaticModal = false;

    $: if (postPubId !== $page.data.postPubId) {
        postPubId = $page.data.postPubId;
        isThisComment = postPubId !== undefined;
        pubId = isThisComment ? postPubId : $page.data.mainPostPubId;
        pubBtnName = isThisComment ? "Comment" : "Post";
    }

    let isPublishing = false;

    const checkIfInputIsInvalid = () => {
        const wordCount = calculateWordCount(userEnteredContent);

        if (userEnteredContent.length === 0) {
            inputInvalidReason = "";
            isInputInvalid = true;
        } else if (wordCount > wordLimit) {
            inputInvalidReason = `Words cannot be more than ${wordLimit}`;
            isInputInvalid = true;
        } else {
            inputInvalidReason = "";
            isInputInvalid = false;
        }
    }

    const calculateWordCount = (content: string) => {
        // Remove HTML tags using a regular expression
        const cleanContent = content.replace(/<\/?[^>]+(>|$)/g, ' ');

        // Remove extra spaces, new lines, and special characters using regex
        const cleanedText = cleanContent.replace(/\s+/g, ' ').trim();

        // Split the cleaned text into words and count the number of words
        const words = cleanedText.split(' ');

        return words.length;
    }

    const handlePaste = async (event: ClipboardEvent) => {
        // Prevent the default paste behavior
        event.preventDefault();

        // Get the pasted text from the clipboard
        const pastedText = (event.clipboardData || window.clipboardData).getData('text/plain');

        // Insert the plain text into the contenteditable div
        const selection = window.getSelection();

        if (selection === null) return;

        if (!selection.rangeCount) return;
        selection.deleteFromDocument();
        selection.getRangeAt(0).insertNode(document.createTextNode(pastedText));

        // Update the userEnteredContent variable with the new content
        const editableDiv = document.getElementById("editableDiv");
        if (editableDiv) {
            userEnteredContent = editableDiv.innerHTML;
        }

        // Perform any necessary checks or validations
        checkIfInputIsInvalid();
    }


    let postThroughUser = async () => {
        if (!checkIsSignedIn()) {
            showLoginModal = true;
        } else {
            isPublishing = true;
            try {
                const txPromise = postAPublication(userEnteredContent, pubId);
                txPromise.then((tx) => {
                    checkUntilPubAdded(tx?.hash, Date.now());
                });
            } catch (err) {
                console.log("error: ", err);
                isPublishing = false;
            }
        }
    };

    const checkUntilPubAdded = async (txHash: string, startTime: number) => {

        /** If post is not added to lens within 25 seconds, then stop checking */
        if (Date.now() - startTime > 25000) {
            isPublishing = false;
            alert("Error adding post");
            return;
        }

        const hasIndexedResponse = await checkTxHashBeenIndexed(txHash);

        if (hasIndexedResponse?.data?.hasTxHashBeenIndexed?.indexed === false) {
            console.log("Waiting for post to be added to graph");
            setTimeout(() => checkUntilPubAdded(txHash, startTime), 100);
        } else {
            isPublishing = false;
            userEnteredContent = "";
            reloadCommentOfAPublication.setReloadCommentOfAPublication(Date.now());
            console.log("Post added to graph" + Date.now());
        }
    };

    const checkIsSignedIn = () => {
        let isSignedInVal;
        const unsubscribe = isSignedIn.subscribe((val) => {
                isSignedInVal = val;
            }
        );
        unsubscribe();

        return isSignedInVal;
    }

    const postAnonymously = async () => {
        const mainPostPubId = $page.data.mainPostPubId;
        const postPubId = $page.data.postPubId;

        console.log(`${pubBtnName} on its way!`);
        addNotification({
            position: 'top-right',
            heading: `${pubBtnName} on its way!`,
            description: `Your anonymous ${pubBtnName.toLowerCase()} is getting ready to shine! Hang tight for a brief moment - your patience is golden!`,
            type: flightTakeoff,
            removeAfter: 7000,
        });

        try {
            const localPubBtnName = pubBtnName
            await fetch('/api/comment-anonymously', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "pubId": $page.data.postPubId !== undefined ? $page.data.postPubId : $page.data.mainPostPubId,
                    "commentContent": userEnteredContent
                })
            }).then((res) => {
                if (res.ok)
                    return res.json();
                else
                    throw new Error(res.statusText);
            });

            console.log("successfully posted anonymously");
            userEnteredContent = "";

            addNotification({
                position: 'top-right',
                heading: `Successfully ${localPubBtnName}ed`,
                description: `Your ${localPubBtnName.toLowerCase()} was successfully ${localPubBtnName.toLowerCase()}ed anonymously. Click on "View ${localPubBtnName}" to see your ${localPubBtnName.toLowerCase()}`,
                type: tick,
                removeAfter: 12000,
                ctaBtnName: `View ${localPubBtnName}`,
                ctaFunction: () => {
                    if (mainPostPubId === $page.data.mainPostPubId &&
                        postPubId === $page.data.postPubId) {
                        //TODO: Make this better
                        window.location.reload();
                    } else {
                        if (postPubId === undefined)
                            goto(`/posts/${mainPostPubId}`);
                        else
                            goto(`/posts/${mainPostPubId}/${postPubId}`);
                    }
                }
            });
        } catch (error) {
            console.log('error', error);
            addNotification({
                position: 'top-right',
                heading: `Failed To ${pubBtnName}`,
                description: `Your ${pubBtnName.toLowerCase()} was not ${pubBtnName.toLowerCase()}ed anonymously. Please try again`,
                type: cross,
                removeAfter: 20000
            });
            throw error;
        }
    }
</script>


<!----------------------------- HTML ----------------------------->
<section>
    <div class="CenterRowFlex body">
        <div class="body__user-pic">
            {#if $isSignedIn}
                <img src={getPictureURL(
                  $userProfile?.picture?.original?.url,
                  $userProfile?.ownedBy
                  )} alt="">
            {:else}
                <img src="https://api.dicebear.com/6.x/bottts-neutral/svg?seed=Buster" alt="">
            {/if}
        </div>
        <div class="body__input">
            <div contenteditable="true"
                 placeholder="What do think about this ?"
                 class="body__input__box"
                 id="editableDiv"
                 bind:innerHTML={userEnteredContent}
                 on:input={checkIfInputIsInvalid}
                 on:paste={handlePaste}
            >
            </div>
            {#if isInputInvalid}
                <div class="body__input__err-msg">{inputInvalidReason}</div>
            {/if}
        </div>
    </div>
    <div class="CenterRowFlex footer">
        <div class="CenterRowFlex footer__insert">
            <!--            <div class="CenterRowFlex footer__insert__item">-->
            <!--                <Icon d={addPhoto}/>-->
            <!--                Photo-->
            <!--            </div>-->
            <button class="footer__insert__item__matic" on:click={() => showGetTestMaticModal = true}>
                Get test MATIC
            </button>
        </div>
        <div class="CenterRowFlex footer__operations">
            <button on:click={postAnonymously}
                    disabled={isInputInvalid}
                    class="btn-alt"
                    style="--btn-alt-color: #1e4748;">
                {pubBtnName} anonymously
            </button>
            {#if !isPublishing}
                <button class="btn" on:click={postThroughUser}
                        disabled={isInputInvalid}>{pubBtnName} as you
                </button>
            {:else}
                <button class="btn"
                        disabled>
                    {pubBtnName}ing &nbsp;<Loader/>
                </button>
            {/if}
        </div>
    </div>
</section>

<Login bind:showLoginModal/>
<GetTestMatic bind:showGetTestMaticModal />
<!---------------------------------------------------------------->


<!----------------------------- STYLE ----------------------------->
<style lang="scss">
  section {
    min-width: 33rem;
  }

  .body {
    background: #18393A;
    padding: 1.3rem;
    gap: 1rem;
    justify-content: space-between;
    border-radius: 10px 10px 0 0;
  }

  .body__user-pic {
    margin-bottom: auto;
  }

  .body__user-pic img {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    border: 2px solid #32F9FF;
  }

  [contenteditable=true]:empty:before {
    content: attr(placeholder);
  }

  .body__input {
    width: 100%;
  }

  .body__input__box {
    content: attr(placeholder);
    width: 100%;
    border-radius: 0.75rem;
    background: linear-gradient(172deg, rgba(50, 249, 255, 0.15) 33.55%, rgba(236, 254, 255, 0.15) 100%);
    padding: 1rem;
      overflow-wrap: anywhere;
  }

  .body__input__err-msg {
    margin-top: 0.7rem;
    color: red;
    font-size: var(--small-font-size);
  }

  .body__input__box:focus {
    border: 2px solid var(--primary);
  }

  .footer {
    background: #1e4748;
    padding: 1rem;
    gap: 1rem;
    justify-content: space-between;
    border-radius: 0 0 10px 10px;
  }

  .footer__insert__item {
    padding: 0.7rem;
    background: #18393a;
    gap: 0.7rem;
    align-items: flex-end;
    border-radius: 7px;
  }

  .footer__insert__item__matic {
      color: var(--primary);
      font-size: var(--small-font-size);
  }

  .footer__operations {
    gap: 1rem;
  }

</style>
<!----------------------------------------------------------------->
