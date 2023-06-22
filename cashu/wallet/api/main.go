package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
)

const (
	BaseURL = "http://localhost:8000" // Assuming API server is running on localhost:8000. Replace with your server address.
)

type Client struct {
	BaseURL    *url.URL
	httpClient *http.Client
}

func NewClient(baseUrlStr string) (*Client, error) {
	baseUrl, err := url.Parse(baseUrlStr)
	if err != nil {
		return nil, err
	}

	client := &Client{
		BaseURL:    baseUrl,
		httpClient: &http.Client{},
	}

	return client, nil
}

// /balance

type BalanceResponse struct {
	Balance int                    `json:"balance"`
	Keysets map[string]interface{} `json:"keysets"`
	Mints   map[string]interface{} `json:"mints"`
}

func (c *Client) Balance() (*BalanceResponse, error) {
	rel := &url.URL{Path: "/balance"}
	u := c.BaseURL.ResolveReference(rel)

	req, err := http.NewRequest("GET", u.String(), nil)
	if err != nil {
		return nil, err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var balanceResponse BalanceResponse
	err = json.NewDecoder(resp.Body).Decode(&balanceResponse)
	if err != nil {
		return nil, err
	}

	return &balanceResponse, nil
}

// /send

type SendResponse struct {
	Balance int    `json:"balance"`
	Token   string `json:"token"`
	Npub    string `json:"npub"`
}

type SendParameters struct {
	Amount  int     `json:"amount"`
	Nostr   *string `json:"nostr"`
	Lock    *string `json:"lock"`
	Mint    *string `json:"mint"`
	NoSplit *bool   `json:"nosplit"`
}

func (c *Client) Send(params SendParameters) (*SendResponse, error) {
	rel := &url.URL{Path: "/send"}
	u := c.BaseURL.ResolveReference(rel)

	values := url.Values{}
	values.Add("amount", strconv.Itoa(params.Amount))

	if params.Nostr != nil {
		values.Add("nostr", *params.Nostr)
	}
	if params.Lock != nil {
		values.Add("lock", *params.Lock)
	}
	if params.Mint != nil {
		values.Add("mint", *params.Mint)
	}
	if params.NoSplit != nil {
		values.Add("nosplit", strconv.FormatBool(*params.NoSplit))
	}

	u.RawQuery = values.Encode()

	req, err := http.NewRequest("POST", u.String(), nil)
	if err != nil {
		return nil, err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var sendResponse SendResponse
	err = json.NewDecoder(resp.Body).Decode(&sendResponse)
	if err != nil {
		return nil, err
	}

	return &sendResponse, nil
}

// /receive

type ReceiveResponse struct {
	InitialBalance int `json:"initial_balance"`
	Balance        int `json:"balance"`
}

type ReceiveParameters struct {
	Token string  `json:"token"`
	Lock  *string `json:"lock"`
	Nostr *bool   `json:"nostr"`
	All   *bool   `json:"all"`
}

func (c *Client) Receive(params ReceiveParameters) (*ReceiveResponse, error) {
	rel := &url.URL{Path: "/receive"}
	u := c.BaseURL.ResolveReference(rel)

	values := url.Values{}
	values.Add("token", params.Token)

	if params.Lock != nil {
		values.Add("lock", *params.Lock)
	}
	if params.Nostr != nil {
		values.Add("nostr", strconv.FormatBool(*params.Nostr))
	}
	if params.All != nil {
		values.Add("all", strconv.FormatBool(*params.All))
	}

	u.RawQuery = values.Encode()

	req, err := http.NewRequest("POST", u.String(), nil)
	if err != nil {
		return nil, err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var receiveResponse ReceiveResponse
	err = json.NewDecoder(resp.Body).Decode(&receiveResponse)
	if err != nil {
		return nil, err
	}

	return &receiveResponse, nil
}

// /invoice

type InvoiceResponse struct {
	Amount  int    `json:"amount"`
	Hash    string `json:"hash"`
	Invoice struct {
		Amount      int    `json:"amount"`
		Pr          string `json:"pr"`
		Hash        string `json:"hash"`
		PaymentHash string `json:"payment_hash"`
		Preimage    string `json:"preimage"`
	} `json:"invoice"`
}

type InvoiceParameters struct {
	Amount int     `json:"amount"`
	Hash   *string `json:"hash"`
	Mint   *string `json:"mint"`
	Split  *int    `json:"split"`
}

func (c *Client) Invoice(params InvoiceParameters) (*InvoiceResponse, error) {
	rel := &url.URL{Path: "/invoice"}
	u := c.BaseURL.ResolveReference(rel)

	values := url.Values{}
	values.Add("amount", strconv.Itoa(params.Amount))

	if params.Hash != nil {
		values.Add("hash", *params.Hash)
	}
	if params.Mint != nil {
		values.Add("mint", *params.Mint)
	}
	if params.Split != nil {
		values.Add("split", strconv.Itoa(*params.Split))
	}

	u.RawQuery = values.Encode()

	req, err := http.NewRequest("POST", u.String(), nil)
	if err != nil {
		return nil, err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var invoiceResponse InvoiceResponse
	err = json.NewDecoder(resp.Body).Decode(&invoiceResponse)
	if err != nil {
		return nil, err
	}

	return &invoiceResponse, nil
}

// /pay

// PayResponse struct corresponds to the successful response from the /pay operation.
type PayResponse struct {
	Amount        int `json:"amount"`
	Fee           int `json:"fee"`
	AmountWithFee int `json:"amount_with_fee"`
}

// PayParameters struct contains the parameters for the /pay operation.
type PayParameters struct {
	Invoice string  `json:"invoice"`
	Mint    *string `json:"mint"`
}

// Pay function sends a request to the /pay endpoint and returns the response.
func (c *Client) Pay(params PayParameters) (*PayResponse, error) {
	rel := &url.URL{Path: "/pay"}
	u := c.BaseURL.ResolveReference(rel)

	values := url.Values{}
	values.Add("invoice", params.Invoice)

	if params.Mint != nil {
		values.Add("mint", *params.Mint)
	}

	u.RawQuery = values.Encode()

	req, err := http.NewRequest("POST", u.String(), nil)
	if err != nil {
		return nil, err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var payResponse PayResponse
	err = json.NewDecoder(resp.Body).Decode(&payResponse)
	if err != nil {
		return nil, err
	}

	return &payResponse, nil
}

func main() {
	api, err := NewClient("http://127.0.0.1:4448")
	if err != nil {
		fmt.Println(err)
		return
	}

	// calling /balance endpoint
	balanceResponse, err := api.Balance()
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println(balanceResponse.Balance)
	}

	// call /send
	noSplit := true
	sendResponse, err := api.Send(SendParameters{
		Amount:  1,
		NoSplit: &noSplit,
	})
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println(sendResponse.Token)
		fmt.Println(sendResponse.Balance)
	}

	// call /receive
	fmt.Println(sendResponse.Token)
	receiveResponse, err := api.Receive(ReceiveParameters{
		Token: sendResponse.Token,
	})
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println(receiveResponse.InitialBalance, receiveResponse.Balance)
	}
}
