namespace OrderFixture;

public record Order
{
    public required string Id { get; init; }

    public required Product Product { get; init; }

    public required int Quantity { get; init; }

    public required string CustomerId { get; init; }

    public required decimal Total { get; init; }
}
