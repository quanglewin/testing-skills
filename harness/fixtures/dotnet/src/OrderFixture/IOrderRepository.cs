namespace OrderFixture;

public interface IOrderRepository
{
    Order Save(Order order);

    Order? FindById(string id);
}
