// Learn more about F# at https://fsharp.org

open System

open FSharp.Data
open FSharp.Text.RegexProvider

open PuppeteerSharp

// CSV Schema that will be used for output later
type ItemInfo =
    CsvProvider<Sample = "Label,  Stars, Ratings, Sold, PriceMin, PriceMax, Stock, Seller, SellerRatings, Products, ResponseRate, ResponseTime, Joined, Followers, URL",
                Schema = "string, float, int,     int,  float,    float,    int,   string, int,           int,      float,        string,       string, int,       string",
                HasHeaders = true>

// Type filter RegEx
type Stock = Regex<(@"(?<Stock>^\d+).piece")>
type Price = Regex<(@"(?<Price>^RM.*\.\d{2})")>
type PriceRange = Regex<(@"(?<PriceMin>^RM.*\.\d{2}).+(?<PriceMax>RM.*\.\d{2})")>

// Get the HTNL data from a Shopee category
let GetShListing (browser :Browser) (url :string) = async {   
    try
        // Simulate user browsing activity to load the similar items listing
        use! page = browser.NewPageAsync () |> Async.AwaitTask
        do! page.GoToAsync (url, WaitUntilNavigation.Networkidle2) |> Async.AwaitTask |> Async.Ignore
        //do! page.ClickAsync @"button.shopee-button-outline" |> Async.AwaitTask |> Async.Ignore
        do! page.ClickAsync "span.shopee-sort-bar__label" |> Async.AwaitTask |> Async.Ignore
        do! page.EvaluateExpressionAsync "window.scrollBy(0, document.body.scrollHeight);" |> Async.AwaitTask |> Async.Ignore
        do! page.WaitForSelectorAsync "footer" |> Async.AwaitTask |> Async.Ignore

        // Return the HTML data captured by the browser
        let! html = page.GetContentAsync () |> Async.AwaitTask
        return Some (html)
    with
    | :? AggregateException as e -> printfn "URL:%s\nError:%s\n" url e.Message
                                    return None
}

// Get the HTNL data from a Shopee listing
let GetShItemInfo (browser :Browser) (url :string) = async {   
    try
        // Simulate user browsing activity to load item data
        use! page = browser.NewPageAsync () |> Async.AwaitTask
        do! page.GoToAsync (url, WaitUntilNavigation.Networkidle2) |> Async.AwaitTask |> Async.Ignore
        //do! page.ClickAsync @"button.shopee-button-outline" |> Async.AwaitTask |> Async.Ignore
        do! page.ClickAsync "div._3Lybjn" |> Async.AwaitTask |> Async.Ignore
        do! page.EvaluateExpressionAsync "window.scrollBy(0, document.body.scrollHeight);" |> Async.AwaitTask |> Async.Ignore
        do! page.WaitForSelectorAsync "footer" |> Async.AwaitTask |> Async.Ignore

        // Return the HTML data captured by the browser
        let! html = page.GetContentAsync () |> Async.AwaitTask
        return Some (html, url)
    with
    | :? AggregateException as e -> printfn "URL:%s\nError:%s\n" url e.Message
                                    return None
}

// Get item URLs from listing
let GetItemURLs output =
    Array.Parallel.map HtmlDocument.Parse output
    |> Array.Parallel.collect (fun x -> x.CssSelect "a[data-sqe='link']" |> Array.ofList)
    |> Array.Parallel.map (fun x -> "https://shopee.com.my" + x.AttributeValue ("href"))

let ToNumber (str :string) = str.ToCharArray () |> Array.filter (fun c -> Char.IsNumber c || c = '.') |> String

let PriceMin price =
    let sprice = match price with
                 | pm when PriceRange().IsMatch (pm) -> PriceRange().TypedMatch(pm).PriceMin.Value                                          
                 | pv when Price().IsMatch (pv) -> Price().TypedMatch(pv).Price.Value
                 | p -> p
    sprice |> ToNumber |> float

let PriceMax price =
    let sprice = match price with
                 | pm when PriceRange().IsMatch (pm) -> PriceRange().TypedMatch(pm).PriceMax.Value
                 | pv when Price().IsMatch (pv) -> Price().TypedMatch(pv).Price.Value
                 | p -> p
    sprice |> ToNumber |> float

let StockFilter (node :list<HtmlNode>) =
    let y = node |> Seq.map (fun x -> x.InnerText().Trim ())
    Stock().TypedMatch(Seq.item 2 y).Stock.Value

let GetKorM (str :string) =
    match str with
    | k when k.Contains ('k') -> (ToNumber k |> float) * 1000.0 |> int
    | m when m.Contains ('m') -> (ToNumber m |> float) * 1000000.0 |> int
    | a -> int a

let GetItemData (output, url) = async {
    let doc = HtmlDocument.Parse output
    let label = doc.CssSelect "div[class='qaNIZv'] > span" |> List.map (fun x -> x.InnerText ())
    let stars = doc.CssSelect "div[class='_3Oj5_n _2z6cUg']" |> List.map (fun x -> x.InnerText () |> float)
    let ratings = doc.CssSelect "div[class='_3Oj5_n']" |> List.map (fun x -> x.InnerText ())
    let sold = doc.CssSelect "div[class='_22sp0A']" |> List.map (fun x -> x.InnerText ())
    let price = doc.CssSelect "div[class='_3n5NQx']" |> List.map (fun x -> x.InnerText ())
    let stock = doc.CssSelect "div.flex.items-center._1FzU2Y > div > div div" |> StockFilter |> int
    let seller = doc.CssSelect "div[class='_3Lybjn']" |> List.map (fun x -> x.InnerText ())
    let sinfo = doc.CssSelect "span._1rsHot" |> List.map (fun x -> x.InnerText ())

    return ItemInfo.Row (
        label.Head,
        (if stars.IsEmpty then 0.0 else stars.Head),
        (if ratings.IsEmpty then 0 else GetKorM ratings.Head),
        (if sold.IsEmpty then 0 else GetKorM sold.Head),
        PriceMin price.Head,
        PriceMax price.Head,
        stock,
        seller.Head,
        GetKorM sinfo.[0],
        GetKorM sinfo.[1],
        (sinfo.[2] |> ToNumber |> float) / 100.0,
        sinfo.[3].Remove (0, 7),
        sinfo.[4].Remove (sinfo.[4].IndexOf "ago"),
        GetKorM sinfo.[5],
        url)
}

// Get a Puppeteer Chromium instance
let GetBrowser revision = async {
    let bfetch = BrowserFetcher ()
    let! rev = bfetch.DownloadAsync revision |> Async.AwaitTask
    // Set viewport and launch options
    let voptions = ViewPortOptions (Width = 1240, Height = 3570)
    let loptions = LaunchOptions (ExecutablePath = rev.ExecutablePath,
                                  DefaultViewport = voptions,
                                  Headless = true)
    // Launch a browser instance
    let! browser = Puppeteer.LaunchAsync loptions |> Async.AwaitTask
    // Close first tab
    let! tabs = browser.PagesAsync () |> Async.AwaitTask
    do! tabs.[0].CloseAsync () |> Async.AwaitTask

    return browser
}

[<EntryPoint>]
let main argv =
    match argv.Length with
    | 3 -> printfn "\n\tDownloading Shopee listing data:"
           printfn "\t%s" argv.[0]
           let range = (int argv.[1]) - 1
           let pages = [|for i in [0..range] -> sprintf "%s?page=%d" argv.[0] i|]

           // Download the Puppeteer Chromium browser
           use browser = GetBrowser 737027 |> Async.RunSynchronously

           // Get a list of items from the product/service category
           let output = (pages |> Array.Parallel.map (fun x -> GetShListing browser x), 4)
                        |> Async.Parallel |> Async.RunSynchronously

           // Parse the HTML data and extract the item urls
           printfn "\tParsing HTML for Item listings..."
           let pages = output |> Array.Parallel.choose id |> GetItemURLs

           // Get each and every item HTML
           printfn "\tDownloading Shopee listing HTML..."
           let output = (pages |> Array.Parallel.map (fun x -> GetShItemInfo browser x), 4)
                        |> Async.Parallel |> Async.RunSynchronously
           
           // Close and exit the browser
           do browser.CloseAsync () |> Async.AwaitTask |> Async.Start

           // Parse the HTML data and extract the item urls
           printfn "\tGenerating CSV data from item listing..."
           let rows = output |> Array.Parallel.choose id |> Array.Parallel.map GetItemData
                      |> Async.Parallel |> Async.RunSynchronously
           
           // Save the generated CSV output into a file
           printfn "\tSaving output into: %s" argv.[2]
           use csv = new ItemInfo (rows)
           csv.Save argv.[2]

    | _ -> printfn "\tURL, Number of Pages and CSV file name required."
           printfn "\tExample: dotnet run https://shopee.com.my/Tickets-Vouchers-cat.173 100 output.csv"
    0 // return an integer exit code
