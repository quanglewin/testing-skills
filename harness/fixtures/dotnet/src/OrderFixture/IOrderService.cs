namespace OrderFixture;

public interface IOrderService
{
    Order CreateOrder(OrderRequest request);

    string ProcessPayment(Order order);

    Order GetOrder(string id);
}
