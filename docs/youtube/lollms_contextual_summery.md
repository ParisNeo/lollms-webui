Hi there, this is a short to show you the potential of the hierarchical contextual summary of documents using lollms.

To do so, we first go to settings page. Under the personalities section, select the category data, and mount the docs_zipper personality.

Now, we go to the personality settings and we set some specific summery parameters. Here we say keep the method description, we select keep document title and authors in the summary. We set the summary size in tokens and we validate.

Now we add the document to summarize and we go to the personality menu and we select start

The document will be decomposed into a certain number of chunks, then each chunk is contextually summarized. After that the summeries are tied together then the operation is repeated until the compressed text is smaller than the maximum number of tokens set in the configuration.

The contextual nature of this algorithm will allow you to have better control over the summary. For example, here we asked for keeping the title, the author names and the results of the paper as well as the method.

As you can see, the summary has respected all the constraints that we did set. We can find the title, the authors names, the method and the numerical results.

Don't forget to like and subscribe
Thanks for watching
