import lume from "lume/mod.ts";
import toc from "https://deno.land/x/lume_markdown_plugins@v0.7.0/toc.ts";
import title from "https://deno.land/x/lume_markdown_plugins@v0.7.0/title.ts";
import footnotes from "https://deno.land/x/lume_markdown_plugins@v0.7.0/footnotes.ts";
import favicon from "lume/plugins/favicon.ts";
import sitemap from "lume/plugins/sitemap.ts";
import date from "lume/plugins/date.ts";
import readInfo from "lume/plugins/reading_info.ts";
import codeHighlight from "lume/plugins/code_highlight.ts";
import lightningCss from "lume/plugins/lightningcss.ts";

const markdown = {}

const site = lume({
  location: new URL("https://nathanfurnal.xyz"),
}, {markdown})
  .use(toc({
    level: 2
  }))
  .use(title())
  .use(footnotes())
  .use(date())
  .use(readInfo())
  .use(favicon())
  .use(sitemap())
  .use(codeHighlight())
  .use(lightningCss());

site.copy("static/fonts", "fonts")

site.data("getYear", () => {
  return new Date().getFullYear();
});

site.ignore("README.md")

export default site;
