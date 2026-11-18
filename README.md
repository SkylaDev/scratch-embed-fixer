# Scratch Embed Fixer
### Another one of my stupid ideas :3


This is a very basic (practicly proof of concept) embed fixer for [scratch.mit.edu](https://scratch.mit.edu/). It simply takes a project URL similar to scratch and will return a viable embed for sites like Discord.

This is achieved via the Scratch public API to fetch basic project information from an ID, its then served as a blank redirect page with said data in [Open Graph protocol](https://ogp.me/) format tags, in theory this can be altered to use [oEmbed](https://oembed.com/) or Twitter Card metadata formats but I prefer to use OGP as it is wider supported and simpler overall.

Feel free to poke around at the code, fork it, print it off and eat it with your Sunday roast I honestly don't care as long as you dont feed it to some stupid LLM and ask it to "make it better" because that doesn't make you a programmer, that makes you a cuck coder... anyways have fun, do whatever and have fun, kthxbai! <3
