<script lang="ts">
    import Icon from "$lib/Icon.svelte";
    import {
        copy,
        cross,
        login,
        modeComment,
        moreVert,
        redirect,
        share,
        thumbDown,
        thumbDownAlt,
        thumbUp,
        thumbUpAlt,
        unfoldMore
    } from "../../utils/frontend/appIcon";
    import RelatedPost from "./RelatedPost.svelte";
    import { page } from "$app/stores";
    import { getPublicationByPubId } from "../../utils/frontend/getPublicationByPubId";
    import getFormattedDate from "../../utils/frontend/getFormattedDate";
    import getImageURLUsingParentPubId from "../../utils/frontend/getImageURLUsingParentPubId";
    import { totalPosts } from "../../services/totalPosts";
    import { getNotificationsContext } from "svelte-notifications";
    import MediaQuery from "$lib/MediaQuery.svelte";
    import { isSignedIn } from "../../services/signInStatus";
    import { addReactionToAPost, removeReactionFromAPost } from "../../utils/frontend/updateReactionForAPost";
    import Login from "../Login.svelte";
    import { onMount } from "svelte";
    import { reloadMainPost } from "../../services/reloadPublication";
    import { metaTagsImageAlt, metaTagsImageUrl, metaTagsTitle } from "../../services/metaTags";


    const {addNotification} = getNotificationsContext();
    let mainPostPubId = $page.data.mainPostPubId;
    let relatedPostsActive = false;
    let showLoginModal = false;
    let reaction: string | null = null;
    let upVoteCount = 0;
    let downVoteCount = 0;

    let promiseOfGetMainPost = getPublicationByPubId(mainPostPubId);

    $: if (mainPostPubId !== $page.data.mainPostPubId) {
        mainPostPubId = $page.data.mainPostPubId;
        promiseOfGetMainPost = getPublicationByPubId(mainPostPubId);
    }

    onMount(() => {
        reloadMainPost.subscribe((val) => {
            console.log("Reloaded main post" + val);
            promiseOfGetMainPost = getPublicationByPubId(mainPostPubId);
        });
    });

    const getTotalPosts = (fetchedTotalPosts: number) => {
        totalPosts.setTotalPosts(fetchedTotalPosts);
        return fetchedTotalPosts;
    }

    const sharePost = (event: Event, id) => {
        event.preventDefault();
        event.stopPropagation();
        navigator.clipboard.writeText(window.location.origin + "/posts/" + id);
        addNotification({
            position: 'top-right',
            heading: 'Copied to clipboard',
            description: 'The link to this post has been copied to your clipboard.',
            type: copy,
            removeAfter: 5000,
        });
    }

    const callAddReaction = async (event: Event, passedReaction: string) => {
        event.preventDefault();
        event.stopPropagation();

        let signedStatus;
        const unsub = isSignedIn.subscribe((value) => {
            signedStatus = value;
        });
        unsub();

        if (!signedStatus) {
            openLoginNotification();
        } else {
            try {
                if (reaction !== null) {
                    await callRemoveReaction(event, reaction);
                }

                reaction = passedReaction;
                upVoteCount = passedReaction === "UPVOTE" ? upVoteCount + 1 : upVoteCount;
                downVoteCount = passedReaction === "DOWNVOTE" ? downVoteCount + 1 : downVoteCount;

                await addReactionToAPost(mainPostPubId, passedReaction);

            } catch (error) {
                console.log("Error while reacting", error);

                addNotification({
                    position: "top-right",
                    heading: "Error while reacting",
                    description: "Please try again .",
                    type: cross,
                    removeAfter: 4000
                });
            }
        }

    };

    const callRemoveReaction = async (event: Event, passedReaction: string) => {
        event.preventDefault();
        event.stopPropagation();

        let signedStatus;
        const unsub = isSignedIn.subscribe((value) => {
            signedStatus = value;
        });
        unsub();

        if (!signedStatus) {
            openLoginNotification();
        } else {
            try {
                reaction = null;
                upVoteCount = passedReaction === "UPVOTE" ? upVoteCount - 1 : upVoteCount;
                downVoteCount = passedReaction === "DOWNVOTE" ? downVoteCount - 1 : downVoteCount;

                await removeReactionFromAPost(mainPostPubId, passedReaction);
            } catch (error) {
                console.log("Error while reacting", error);

                addNotification({
                    position: "top-right",
                    heading: "Error removing",
                    description: "Error while removing your reaction. Please try again .",
                    type: cross,
                    removeAfter: 4000
                });
            }
        }

    };

    const openLoginNotification = () => {
        addNotification({
            position: "top-right",
            heading: "Please Login",
            description: "Kindly log-in to react to this post. Simply click on \"Login\" button to proceed with your login.",
            type: login,
            removeAfter: 10000,
            ctaBtnName: "Login",
            ctaFunction: () => {
                showLoginModal = true;
            }
        });
    };

    const updateReactionDetails = (
      passedReaction: string,
      passedUpVoteCount: number,
      passedDownVoteCount: number) => {
        reaction = passedReaction;
        upVoteCount = passedUpVoteCount;
        downVoteCount = passedDownVoteCount;
        return "";
    };

    const updateMetaTagsTitle = (webPageUrl: string) => {
        const domain = new URL(webPageUrl).hostname.replace("www.", "");
        metaTagsTitle.setMetaTagsTitle(`${domain} | LensView`);
        metaTagsImageAlt.setMetaTagsImageAlt(`${domain} webpage image`);
        return "";
    };

    const updateMetaTagsImageUrl = (imageUrl: string) => {
        metaTagsImageUrl.setMetaTagsImageUrl(imageUrl);
        return "";
    };
</script>


<!----------------------------- HTML ----------------------------->
<MediaQuery query="(max-width: 1024px)" let:matches>
    {#if matches}
        <section class="tablet">
            {#await promiseOfGetMainPost}
                <div class="CenterColumnFlex tablet__main-post__loader">
                    <div class="tablet__main-post__image__loader"></div>
                    <div class="CenterRowFlex tablet__main-post__url__loader"></div>
                    <div class="tablet__main-post__info__loader"></div>
                </div>
                {#if relatedPostsActive}
                    <div class="CenterRowFlex h3 tablet__related-posts">
                        <div class="tablet__related-posts__title">
                            Related Posts
                        </div>
                        <button on:click={() => relatedPostsActive = false}>
                            <Icon d={cross}/>
                        </button>
                    </div>
                    <div class="related-posts-body">
                        <RelatedPost
                                userEnteredUrl={'https://www.youtube.com/watch?app=desktop&v=Fmr0auKkgbk&pp=ygUJdGVjaHdpc2Vy'}/>
                    </div>
                {:else}
                    <button on:click={() => relatedPostsActive = true}
                            class="tablet__related-posts-toggle">
                        Related Posts
                        <Icon d={unfoldMore} size="2em"/>
                    </button>
                {/if}
            {:then mainPostPub}
                <a href={`/posts/${mainPostPubId}`} class="tablet__main-post">
                    {#await getImageURLUsingParentPubId(mainPostPub?.data?.publications?.items[0]?.id)}
                        <div class="tablet__main-post__image__loader"></div>
                    {:then imageUrl}
                        {updateMetaTagsImageUrl(imageUrl)}
                        <div class="tablet__main-post__image">
                            <img src={imageUrl} alt="">
                        </div>
                    {/await}
                    <a class="CenterRowFlex tablet__main-post__url"
                       href={mainPostPub?.data?.publications?.items[0]?.metadata.content}
                       target="_blank"
                    >
                        {updateMetaTagsTitle(mainPostPub?.data?.publications?.items[0]?.metadata.content)}
                        <Icon d={redirect}/>
                        {mainPostPub?.data?.publications?.items[0]?.metadata.content.substring(0, 40)}
                        ...
                    </a>
                    <div class="tablet__main-post__info">
                        <div class="tablet__main-post__info__top">
                            <div class="CenterRowFlex tablet__main-post__info__top__reaction">
                                {updateReactionDetails(
                                  mainPostPub?.data?.publications?.items[0]?.reaction,
                                  mainPostPub?.data?.publications?.items[0]?.stats?.totalUpvotes,
                                  mainPostPub?.data?.publications?.items[0]?.stats?.totalDownvotes
                                )}
                                {#if reaction === "UPVOTE"}
                                    <button on:click={() => callRemoveReaction(event, "UPVOTE")}
                                            class="CenterRowFlex tablet__main-post__info__top__reaction__val">
                                        <Icon d={thumbUp} />
                                        {upVoteCount}
                                    </button>
                                {:else}
                                    <button on:click={() => callAddReaction(event, "UPVOTE")}
                                            class="CenterRowFlex tablet__main-post__info__top__reaction__val">
                                        <Icon d={thumbUpAlt} />
                                        {upVoteCount}
                                    </button>
                                {/if}
                                <div class="tablet__main-post__info__top__reaction__vertical-line"></div>
                                {#if reaction === "DOWNVOTE"}
                                    <button on:click={() => callRemoveReaction(event, "DOWNVOTE")}
                                            class="CenterRowFlex tablet__main-post__info__top__reaction__val">
                                        <Icon d={thumbDown} />
                                        {downVoteCount}
                                    </button>
                                {:else}
                                    <button on:click={() => callAddReaction(event, "DOWNVOTE")}
                                            class="CenterRowFlex tablet__main-post__info__top__reaction__val">
                                        <Icon d={thumbDownAlt} />
                                        {downVoteCount}
                                    </button>
                                {/if}
                            </div>
                            <div class="CenterRowFlex tablet__main-post__info__top__posts-count">
                                <Icon d={modeComment}/>
                                {getTotalPosts(mainPostPub?.data?.publications?.items[0]?.stats?.totalAmountOfComments)}
                            </div>
                            <button on:click={() => sharePost(event, $page.data.mainPostPubId)}
                                    class="CenterRowFlex main-post__content__bottom__share">
                                <Icon d={share}/>
                            </button>
                        </div>
                        <div class="tablet__main-post__info__bottom">
                            <div class="tablet__main-post__info__bottom__label">
                                Added by:
                            </div>
                            <div class="tablet__main-post__info__bottom__added-by__handle">
                                {mainPostPub?.data?.publications?.items[0]?.metadata?.attributes[0]?.value}
                            </div>
                            <div class="tablet__main-post__info__bottom__time">
                                {getFormattedDate(mainPostPub?.data?.publications?.items[0]?.createdAt)}
                            </div>
                        </div>
                    </div>
                </a>
                {#if relatedPostsActive}
                    <div class="CenterRowFlex h3 tablet__related-posts">
                        <div class="tablet__related-posts__title">
                            Related Posts
                        </div>
                        <button on:click={() => relatedPostsActive = false}>
                            <Icon d={cross}/>
                        </button>
                    </div>
                    <div class="related-posts-body">
                        <RelatedPost
                                userEnteredUrl={mainPostPub?.data?.publications?.items[0]?.metadata?.content}/>
                    </div>
                {:else}
                    <button on:click={() => relatedPostsActive = true}
                            class="tablet__related-posts-toggle">
                        Related Posts
                        <Icon d={unfoldMore} size="2em"/>
                    </button>
                {/if}
            {/await}
        </section>
    {:else}
        <section>
            {#await promiseOfGetMainPost}
                <div class="main-post">
                    <div class="main-post__content__loader"></div>
                </div>
                <div class="h2 related-posts-head">
                    Related Posts
                </div>
                <div class="related-posts-body">
                    <RelatedPost userEnteredUrl={""}/>
                </div>
            {:then mainPostPub}
                {#await getImageURLUsingParentPubId(mainPostPub?.data?.publications?.items[0]?.id)}
                    <div class="image__loader"></div>
                {:then imageUrl}
                    {updateMetaTagsImageUrl(imageUrl)}
                    <a href={`/posts/${mainPostPubId}`}>
                        <img src={imageUrl} alt="">
                    </a>
                {/await}
                <div class="CenterColumnFlex main-post">
                    <a href={`/posts/${mainPostPubId}`}
                       class="CenterColumnFlex main-post__content">
                        <div class="CenterRowFlex main-post__content__top">
                            <a href={mainPostPub?.data?.publications?.items[0]?.metadata.content}
                               target="_blank"
                               class="CenterRowFlex"
                            >
                                {updateMetaTagsTitle(mainPostPub?.data?.publications?.items[0]?.metadata.content)}
                                <div class="CenterRowFlex main-post__content__top__redirect">
                                    <Icon d={redirect}/>
                                </div>
                                <div class="main-post__content__top__url">
                                    &nbsp;&nbsp;{mainPostPub?.data?.publications?.items[0]?.metadata.content.substring(0, 40)}
                                    ...
                                </div>
                            </a>
                            <div class="main-post__content__top__time">
                                {getFormattedDate(mainPostPub?.data?.publications?.items[0]?.createdAt)}
                            </div>
                            <div class="CenterRowFlex main-post__content__top__more">
                                <Icon d={moreVert}/>
                            </div>
                        </div>
                        <div class="CenterRowFlex main-post__content__bottom">
                            <div class="CenterRowFlex main-post__content__bottom__reaction">
                                {updateReactionDetails(
                                  mainPostPub?.data?.publications?.items[0]?.reaction,
                                  mainPostPub?.data?.publications?.items[0]?.stats?.totalUpvotes,
                                  mainPostPub?.data?.publications?.items[0]?.stats?.totalDownvotes
                                )}
                                {#if reaction === "UPVOTE"}
                                    <button on:click={() => callRemoveReaction(event, "UPVOTE")}
                                            class="CenterRowFlex main-post__content__bottom__reaction__val">
                                        <Icon d={thumbUp} />
                                        {upVoteCount}
                                    </button>
                                {:else}
                                    <button on:click={() => callAddReaction(event, "UPVOTE")}
                                            class="CenterRowFlex main-post__content__bottom__reaction__val">
                                        <Icon d={thumbUpAlt} />
                                        {upVoteCount}
                                    </button>
                                {/if}
                                <div class="main-post__content__bottom__reaction__vertical-line"></div>
                                {#if reaction === "DOWNVOTE"}
                                    <button on:click={() => callRemoveReaction(event, "DOWNVOTE")}
                                            class="CenterRowFlex main-post__content__bottom__reaction__val">
                                        <Icon d={thumbDown} />
                                        {downVoteCount}
                                    </button>
                                {:else}
                                    <button on:click={() => callAddReaction(event, "DOWNVOTE")}
                                            class="CenterRowFlex main-post__content__bottom__reaction__val">
                                        <Icon d={thumbDownAlt} />
                                        {downVoteCount}
                                    </button>
                                {/if}
                            </div>
                            <div class="CenterRowFlex main-post__content__bottom__posts-count">
                                <Icon d={modeComment}/>
                                {getTotalPosts(mainPostPub?.data?.publications?.items[0]?.stats?.totalAmountOfComments)}
                                &nbsp;Posts
                            </div>
                            <button on:click={() => sharePost(event,$page.data.mainPostPubId)}
                                    class="CenterRowFlex main-post__content__bottom__share">
                                <Icon d={share}/>
                            </button>
                            <div class="CenterRowFlex main-post__content__bottom__added-by">
                                <div class="main-post__content__bottom__added-by__label">
                                    Added by:
                                </div>
                                <div class="main-post__content__bottom__added-by__handle">
                                    {mainPostPub?.data?.publications?.items[0]?.metadata?.attributes[0]?.value}
                                </div>
                            </div>
                        </div>
                    </a>
                </div>
                <div class="h2 related-posts-head">
                    Related Posts
                </div>
                <div class="related-posts-body">
                    <RelatedPost userEnteredUrl={mainPostPub?.data?.publications?.items[0]?.metadata?.content}/>
                </div>
            {/await}
        </section>
    {/if}
</MediaQuery>

<Login bind:showLoginModal />
<!---------------------------------------------------------------->


<!----------------------------- STYLE ----------------------------->
<style lang="scss">
  .tablet {
    display: flex;
    flex-direction: column;
    padding-top: 0;
    //gap: 1rem;
    border-bottom: 1.5px solid #3f494e;
    padding-bottom: 1rem;
  }

  .tablet__main-post {
    background: #123439;
    border-radius: 10.8px;
  }

  .tablet__main-post__loader {
    background: #123439;
    width: 100%;
    border-radius: 10.8px;
  }

  .tablet__main-post__image {
    height: 30rem;
    overflow: auto;
    border-radius: 10.8px;
  }

  .tablet__main-post__image__loader {
    height: 30rem;
    width: 100%;
    border-radius: 10.8px;
  }

  .tablet__main-post__url {
    padding: 0.75rem;
    background: #123439;
    justify-content: flex-start;
    gap: 0.5rem;
  }

  .tablet__main-post__url__loader {
    height: 2rem;
    width: 95%;
    margin: 1rem 1rem 0 1rem;
    border-radius: 10.8px;
  }

  .tablet__main-post__info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.75rem;
    background: #164146;
    border-radius: 0 0 10.8px 10.8px;
  }

  .tablet__main-post__info__loader {
    width: 95%;
    height: 4rem;
    border-radius: 10.8px;
    margin: 1rem;
  }

  .tablet__main-post__info__top {
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
  }

  .tablet__main-post__info__top__reaction {
    background: #13353a;
    border-radius: 6.8px;
    opacity: 70%;
  }

  .tablet__main-post__info__top__reaction__val {
      padding: 0.5rem 0.7rem;
    gap: 0.4rem;
  }

  .tablet__main-post__info__top__reaction__vertical-line {
    border-left: 2px solid #ffffff45;
    height: 21px;
  }

  .tablet__main-post__info__top__posts-count {
    background: #13353a;
    padding: 0.5rem 0.7rem;
    gap: 0.5rem;
    border-radius: 5.8px;
    opacity: 85%;
  }

  .tablet__main-post__info__bottom {
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
    padding: 0.5rem;
    align-items: center;
  }

  .tablet__main-post__info__bottom__label {
    font-size: var(--small-font-size);
    color: var(--text-accent);
  }

  .tablet__main-post__info__bottom__added-by__handle {
    padding: 0.2rem 0.5rem;
    background: #18393a;
    border-radius: 5px;
    color: var(--primary);
  }

  .tablet__main-post__info__bottom__time {
    margin-left: auto;
    font-size: var(--small-font-size);
    color: var(--text-accent);
  }

  .tablet__related-posts {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 1rem;
    margin-top: 1rem;
  }

  .tablet__related-posts-toggle {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #164146;
    border-radius: 10.8px;
    margin-top: 1rem;
  }


  section {
    padding-top: 2rem;
  }

  section img {
    width: 100%;
    border-radius: 10px;
  }

  .image__loader {
    width: 100%;
    border-radius: 10px;
    height: 40rem;
  }

  .main-post {
    height: 10rem;
    width: 100%;
    position: sticky;
    top: 0;
    bottom: 0;
    margin: auto;
    background: rgba(13, 23, 29, 0.50);
    backdrop-filter: blur(8.5px);
    padding: 1.3rem 2rem;
    z-index: 10;
  }

  .main-post__content {
    width: 100%;
    min-width: 34rem;
  }

  .main-post__content__loader {
    width: 100%;
    min-width: 31rem;
    border-radius: 10.8px;
    height: 8rem;
  }

  .main-post__content__top {
    background: #18393a;
    padding: 1rem;
    gap: 0.5rem;
    width: 100%;
    border-radius: 10px 10px 0 0;

  }

  .main-post__content__top__time {
    font-size: var(--small-font-size);
    color: var(--text-accent);
    margin-left: auto;
  }

  .main-post__content__bottom {
    background: #1e4748;
    padding: 1rem;
    gap: 0.5rem;
    width: 100%;
    border-radius: 0 0 10px 10px;
  }

  .main-post__content__bottom__reaction {
    background: #18393a;
    border-radius: 6.8px;
    opacity: 70%;
  }

  .main-post__content__bottom__reaction__val {
      padding: 0.5rem 0.7rem;
    gap: 0.4rem;
  }

  .main-post__content__bottom__reaction__vertical-line {
    border-left: 2px solid #ffffff45;
    height: 21px;
  }

  .main-post__content__bottom__posts-count {
    background: #18393a;
    padding: 0.5rem 0.7rem;
    gap: 0.5rem;
    border-radius: 5.8px;
    opacity: 85%;
  }

  .main-post__content__bottom__share {
    border-radius: 50%;
    background: #18393a;
    padding: 0.5rem;
  }

  .main-post__content__bottom__added-by {
    margin-left: auto;
    gap: 0.5rem;
  }

  .main-post__content__bottom__added-by__label {
    color: var(--text-accent);
  }

  .main-post__content__bottom__added-by__handle {
    padding: 0.2rem 0.5rem;
    background: #18393a;
    border-radius: 5px;
    color: var(--primary);
  }

  .related-posts-head {
    position: sticky;
    top: 10rem;
    background: #0d171d;
    padding: 1.5rem;
    z-index: 10;
  }

  @keyframes shine {
    to {
      background-position-x: -200%;
    }
  }

  .tablet__main-post__image__loader,
  .tablet__main-post__url__loader,
  .tablet__main-post__info__loader,
  .image__loader,
  .main-post__content__loader {
    background: linear-gradient(110deg, #0d9397 8%, #63bdc8 18%, #0d9397 33%);
    background-size: 200% 100%;
    animation: 1s shine linear infinite;
  }
</style>
<!----------------------------------------------------------------->
