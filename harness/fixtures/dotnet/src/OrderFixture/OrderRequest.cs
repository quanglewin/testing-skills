namespace OrderFixture;

public record OrderRequest
{
    public required string ProductId { get; init; }

    public required int Quantity { get; init; }

    public required string CustomerId { get; init; }

    public decimal UnitPrice { get; init; }
}
