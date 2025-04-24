(event_data) => {
    const event = new MessageEvent(
        'message',
        {
            data: event_data,
            origin: "https://challenges.cloudflare.com"
        }
    )
    window.dispatchEvent(event)
}
