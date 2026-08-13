namespace OrderFixture;

public class OrderService(IOrderRepository orderRepository, IPaymentGateway paymentGateway) : IOrderService
{
    private const decimal DiscountThreshold = 100m;
    private const decimal DiscountRate = 0.10m;

    public Order CreateOrder(OrderRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.ProductId))
        {
            throw new ArgumentException("ProductId must not be null or empty.", nameof(request));
        }

        if (request.Quantity <= 0)
        {
            throw new ArgumentException("Quantity must be greater than zero.", nameof(request));
        }

        decimal total = CalculateDiscount(request.UnitPrice * request.Quantity);

        var order = new Order
        {
            Id = Guid.NewGuid().ToString(),
            Product = new Product(request.ProductId, request.UnitPrice),
            Quantity = request.Quantity,
            CustomerId = request.CustomerId,
            Total = total,
        };

        return orderRepository.Save(order);
    }

    public string ProcessPayment(Order order)
    {
        bool approved;
        try
        {
            approved = paymentGateway.Charge(order.CustomerId, order.Total);
        }
        catch (TimeoutException ex)
        {
            throw new PaymentFailedException($"Payment for order '{order.Id}' timed out.", ex);
        }

        if (!approved)
        {
            throw new PaymentFailedException($"Payment for order '{order.Id}' was declined.");
        }

        return $"receipt-{order.Id}";
    }

    public Order GetOrder(string id)
    {
        return orderRepository.FindById(id) ?? throw new OrderNotFoundException(id);
    }

    private static decimal CalculateDiscount(decimal total)
    {
        return total >= DiscountThreshold ? total * (1 - DiscountRate) : total;
    }
}
