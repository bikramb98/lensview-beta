import type { LoadEvent } from "@sveltejs/kit";
import { userEnteredURL } from "../../../services/userEnteredURL";
import { isMainPostAdded } from "../../../services/isPostAddedToLensGraph";
import { getCommentOfPublication } from "../../../utils/frontend/getCommentOfPublication";
import { fetchPublication } from "../../../utils/frontend/fetchPublication";

export async function load({ fetch, params, depends }: LoadEvent) {
  depends("posts: updated-posts");

  const postInfo: string[] | undefined = params.postsInfo?.split("/");
  let hashedURL;
  let commentPubId;

  if (postInfo !== undefined) {
    hashedURL = postInfo[0];
    commentPubId = postInfo[1];
  }

  if (commentPubId !== undefined) {
    console.log("commentPubId" + commentPubId);
    const comments = await getCommentOfPublication(commentPubId);
    console.log("comment", comments);

    const publicationResponse = await fetchPublication(commentPubId);
    console.log("publication", publicationResponse);

    const res = await fetch(`/api/get-url?hashedURL=${hashedURL}`);
    const getURLResponse = await res.json();
    return {
      "hashedURL": hashedURL,
      "URL": getURLResponse["source_url"],
      "items": comments?.data?.publications?.items,
      "pubId": commentPubId,
      "pub": publicationResponse?.data?.publications?.items[0],
      "openCommentSection": true
    };
  }


  const res = await fetch(`/api/posts?hashedURL=${hashedURL}`);
  const fetchedMainPostData = await res.json();

  console.log("fetchedMainPostData", fetchedMainPostData);

  if (fetchedMainPostData["error"] != null) {
    let enteredURL;
    const unsub = userEnteredURL.subscribe((url) => {
      enteredURL = url;
    });
    unsub();

    return {
      "hashedURL": hashedURL,
      "URL": enteredURL,
      "items": [],
      "pubId": "",
      "openCommentSection": false
    };
  }

  console.log("No error");
  isMainPostAdded.set(true);

    return {
      "hashedURL": hashedURL,
      "URL": fetchedMainPostData["URL"],
      "items": fetchedMainPostData["items"],
      "pubId": fetchedMainPostData["parentPublicationID"],
      "openCommentSection": false
    };

}
